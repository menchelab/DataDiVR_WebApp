import multiprocessing as mp
import os
import signal
import time

import GlobalData as GD
import uploader
from project import Project

from . import util

IGNORE_PROJECTS = ["process"]


class AnnotationJob:
    def __init__(self, project, data_type):
        self.project = project
        self.data_type = data_type

    def get_data(self):
        return self.project, self.data_type


class AnnotationScraper:
    def __init__(
        self,
        send_result,
        bp,
    ):
        self.manager = mp.Manager()
        self.queue = self.manager.Queue()
        self.results = self.manager.Queue()
        self.done = self.manager.Value("done", False)
        self.queue_lock = self.manager.Lock()
        self.idle_dict = self.manager.dict()
        self.file_locks = {}
        self.pool = None
        self.forced = False
        self.pool_args = []
        self.handled_projects = {}
        self.handled_anno_requests = {}
        self.projects = [pro for pro in GD.listProjects() if pro not in IGNORE_PROJECTS]
        self.annotations = {}
        self.is_active = False
        self.is_initialized = False
        self.send_result = send_result
        self.blueprint = bp

    def init_pool(self, n=None):
        if n is None:
            n = len(self.projects)
        if n > os.cpu_count() - 5:
            n = os.cpu_count() - 5
        if n < 1:
            n = 1
        bg_args = (
            [
                self.queue,
                self.results,
                self.done,
                self.queue_lock,
                self.file_locks,
                self.idle_dict,
                backup,
            ]
            for backup in [True] + [False] * (n - 1)
        )

        self.pool = mp.Pool(n)
        for _ in range(n):
            self.pool.starmap_async(worker_task, bg_args)
        # for args in bg_args:
        #     worker_task(*args)
        self.is_initialized = True

    def update_annotations(
        self, project, data_type: str or list[str] = ["node", "link"]
    ):
        if isinstance(data_type, str):
            data_type = [data_type]
        for dt in data_type:
            self.add_to_queue(project, dt, force=True)

    def reorganize_queue(self, project, data_type):
        with self.queue_lock:
            jobs = []
            while not self.queue.empty():
                jobs.append(self.queue.get())

            project_idx = None
            for idx, job in enumerate(jobs):
                if job.project == project and job.data_type == data_type:
                    project_idx = idx
                    break
            if project_idx is None:
                jobs.append(AnnotationJob(project, data_type))
            else:
                jobs = [jobs[idx]] + jobs[:idx] + jobs[idx + 1 :]

            for job in jobs:
                self.queue.put(job)

    def add_to_queue(self, project, data_type, force=False):
        processed = self.is_processed(project, data_type)
        processing = self.is_processing(project, data_type)
        project = Project(project).get_origin()
        if not processing or not processed or force:
            if project not in self.file_locks:
                self.file_locks[project] = self.manager.Lock()

            self.set_processed(project, data_type, False)
            self.forced = force

            if force:
                self.reorganize_queue(project, data_type)
            else:
                self.queue.put(AnnotationJob(project, data_type))

        elif processed:
            self.set_processed(project, data_type, True)
            return

        if not self.is_active:
            self.start()

    def get_annotation(self, project_name, data_type):
        processed = self.is_processed(project_name, data_type)
        if processed:
            project = Project(project_name)
            project.name = project.get_origin()

            if project.name not in self.file_locks:
                self.file_locks[project.name] = self.manager.Lock()

            with self.file_locks[project.name]:
                annotations = Project(project_name).get_annotations(data_type)
            # annotations = self.annotations[project_name]
            return annotations[data_type]

        elif self.is_processing(project_name, data_type):
            print(
                f"Request for {data_type} annotations of project {project_name} is processing.."
            )
            while True:
                # print("Waiting for annotations..", project_name, data_type)
                if self.is_processed(project_name, data_type):
                    break
                time.sleep(2)
        else:
            print(
                f"Request to update Annotations of {data_type} data of project {project_name}"
            )
            self.update_annotations(project_name, data_type)
        return self.get_annotation(project_name, data_type)

    def add_result_to_global_data(self, res):
        if res is None:
            return
        project = res["project"]
        data_type = res["type"]
        if project in self.annotations:
            if data_type not in self.annotations[project]:
                # print("Adding result to global data..", project, data_type)
                self.annotations[project][data_type] = res

    def store_result(self, res):
        annotations = {}
        if res is None:
            return

        project_name = res["project"]
        if project_name not in annotations:
            annotations[project_name] = {}

        data_type = res["type"]
        if data_type not in annotations[project_name]:
            annotations[project_name][data_type] = res["annotations"]

        project = Project(project_name, False)
        if project_name not in self.file_locks:
            self.file_locks[project_name] = self.manager.Lock()
        with self.file_locks[project_name]:
            project.read_annotations()

        updated = []
        for data_type in annotations[project_name]:
            project.annotations[data_type] = annotations[project_name][data_type]
            updated.append(data_type)
            project.write_annotations()

        for data_type in updated:
            self.set_processed(project_name, data_type)
            self.send_update_to_clients(project_name, data_type)

    def send_update_to_clients(self, project, data_type):
        message = {
            "project": project,
            "type": data_type,
            "data": "annotations",
            "annotations": self.get_annotation(project, data_type),
        }
        self.send_result(self.blueprint, message)

    def set_processed(self, project, data_type, is_processed=True):
        if project not in self.handled_projects:
            self.handled_projects[project] = {}
        self.handled_projects[project][data_type] = is_processed

    def start(self, delay=0):
        if self.is_active:
            return
        while delay > 0:
            if self.forced:
                break
            time.sleep(5)
            delay -= 5

        try:
            s = time.time()
            self.done.value = False
            self.is_active = True
            for project in self.projects:
                self.update_annotations(project)
            if not self.is_initialized:
                self.init_pool()
            self.idle_dict["main"] = False
            waiter = ["/", "\\"]
            i = 0
            while True:
                print(f"Annotation Scraper: Waiting for results {waiter[i]}", end="\r")
                i = (i + 1) % 2
                if self.results.empty():
                    time.sleep(0.5)
                    continue
                self.store_result(self.results.get())
                with self.queue_lock:
                    if self.queue.empty() and self.all_projects_processed():
                        break
            print(
                "Annotation Scraper: All annotations updated, will terminate...",
                end="\r",
            )
            self.stop()
            print()
            print("=" * 50)
            print("All annotations scraped!")
            print(f"Runtime\t{time.time() - s} s.")
            print("=" * 50)
        except KeyboardInterrupt:
            print("Annotation Scraper: Terminating...")
            self.stop(True)

    def stop(self, terminate=False):
        self.done.value = True
        self.idle_dict["main"] = True
        if terminate:
            self.pool.terminate()
            self.is_initialized = False
        # else:
        #     self.pool.close()
        while True:
            if all(list(self.idle_dict.values())):
                break
            time.sleep(0.5)
        print("Annotation Scraper: All worker done, will handle remaining results...")
        while not self.results.empty():
            self.store_result(self.results.get())
        self.forced = False
        self.is_active = False

    def all_projects_processed(self):
        for project in self.projects:
            for data_type in ["node", "link"]:
                if not self.is_processed(project, data_type):
                    return False
        return True

    def is_processing(self, project, data_type) -> tuple[bool, str]:
        project = Project(project).get_origin()
        if not Project(project).exists():
            return True

        if self.is_processed(project, data_type):
            return True

        if project not in self.handled_projects:
            return False

        if data_type not in self.handled_projects[project]:
            return False

        return True

    def is_processed(self, project: str, data_type: str):
        project = Project(project).get_origin()
        if not Project(project).exists():
            return True

        if project in self.handled_projects:
            if data_type in self.handled_projects[project]:
                if self.handled_projects[project][data_type]:
                    return True

        project = Project(project)

        if project.name not in self.file_locks:
            self.file_locks[project.name] = self.manager.Lock()

        with self.file_locks[project.name]:
            project.read_annotations()

        if project.annotations[data_type] is not None:
            self.set_processed(project.name, data_type)
            return True

        return False

    def request_is_handled(self, project: str, data_type: str):
        project = Project(project).get_origin()

        if project not in self.handled_anno_requests:
            return False
        if data_type not in self.handled_anno_requests[project]:
            return False

        return self.handled_anno_requests[project][data_type]

    def handle_request(self, project, data_type, handling=True):
        if project not in self.handled_anno_requests:
            self.handled_anno_requests[project] = {}

        self.handled_anno_requests[project][data_type] = handling

    def wait_for_annotation(self, message):
        project = message.get("project")
        data_type = message.get("type")
        print("Received request for", project, data_type)
        if project in IGNORE_PROJECTS:
            print("Ignoring request for", project, data_type)
            return

        # if self.request_is_handled(project, data_type):
        #     return

        # self.handle_request(project, data_type)

        message["annotations"] = self.get_annotation(project, data_type)
        message["project"] = project
        message["data"] = "annotations"
        # print(message)
        # self.handle_request(project, data_type, False)
        return message


class Worker(mp.Process):
    def __init__(self, queue, results, done, queue_lock, file_locks, idle_dict, backup):
        super().__init__()
        self.queue = queue
        self.results = results
        self.done = done
        self.queue_lock = queue_lock
        self.file_locks = file_locks
        self.backup = backup
        self.idle_dict = idle_dict
        self.idle(False)

    def idle(self, idle=True):
        self.idle_dict[mp.current_process().pid] = idle

    def remove_from_pool(self):
        self.idle_dict.pop(mp.current_process().pid)

    def run(self):
        # print(f"Starting worker background={self.background}")
        while True:
            if self.done.value:
                break
            if self.queue.empty():
                # break
                # print("Queue empty, waiting..", end="\r")
                time.sleep(0.3)
                continue
            self.collect_annotations()
        # print(f"Worker done: background={self.background}")

    def collect_annotations(self):
        """Collects all the annotations of every project and stores them in the GlobalData."""
        with self.queue_lock:
            job = self.queue.get()
            project, data_type = job.get_data()

        message = {"project": project, "type": data_type}

        # Check if the project might already have be annotated
        project = Project(project)

        with self.file_locks[project.name]:
            project.read_annotations()

        if data_type in project.annotations:
            if project.annotations[data_type]:
                message["annotations"] = project.annotations[data_type]
                self.results.put(message)

        message["annotations"] = util.process_annotation(message, {})
        self.results.put(message)

    def collect_args(self, project, data_type):
        project = Project(project)
        tmp = Project(project.name)
        if project.origin:
            project = self.find_data_origin(tmp, data_type)
        return project.name, data_type


def find_data_origin(project, data_type):
    function_call = {
        "node": project.has_own_nodes,
        "link": project.has_own_links,
    }
    if data_type in function_call:
        if not function_call[data_type]():
            project = Project(project).get_origin()
        return project


def worker_task(*args):
    worker = Worker(*args)
    while True:
        if worker.done.value and worker.queue.empty():
            worker.idle(True)
            time.sleep(5)
            continue
        worker.idle(False)
        worker.run()
        if not worker.backup:
            worker.remove_from_pool()
            break
