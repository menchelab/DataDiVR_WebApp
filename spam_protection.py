"""
Module to monitor UI Spam
""" 
import functools
import threading


### consts
SPAM_MAX_TASKS = 3
# number of expensive tasks until the system shuts them down

SPAM_EXPENSIVE_IDS = {
    'analyticsDegreeRun', 'analyticsClosenessRun', 'analyticsPathRun', 'analyticsEigenvectorRun', 'analyticsModcommunityRun', 'analyticsModcommunityLayout', 'analyticsClusteringCoeffRun', 
    'annotationRun',
    'layoutRandomApply', 'layoutEigenApply', 'layoutCartoLocalApply', 'layoutCartoGlobalApply', 'layoutCartoImportanceApply', 'layoutSpectralApply'
}
# IDs of socket connection which reponse to expensive task requests


### functional part
class SpamProtector:
    def __init__(self):
        self.spam_counter = 0
        self.lock = threading.Lock()

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request_id = ""
            result = None
            request_message = {}
            for arg in args:
                if isinstance(arg, dict):
                    request_message = arg
                    break
            
            if "id" in request_message.keys():
                request_id = request_message["id"]

            if request_id not in SPAM_EXPENSIVE_IDS:
                return func(*args, **kwargs)

            with self.lock:
                if self.spam_counter >= SPAM_MAX_TASKS:
                    print(f"SPAM PROTECTION: Maximum of spam protected requests reached. Shutting down call of: {request_id}.")
                    return

                self.spam_counter += 1

            try:
                result = func(*args, **kwargs)
            except Exception as spam_exc:
                print(f"SPAM PROTECTION: A spam_protected request {request_id} threw exception: {spam_exc}")
            finally:
                with self.lock:
                    self.spam_counter -= 1

            return result

        return wrapper


def spam_debug(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("...........", *args)

        return func(*args, **kwargs)
    return wrapper