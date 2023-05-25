import multiprocessing
import unittest
import time
import os
from skywalking.trace.global_id import GlobalIdGenerator, ID


class TestGlobalIdGenerator(unittest.TestCase):
    def test_refresh_process_id(self):
        old_id = GlobalIdGenerator.PROCESS_ID
        GlobalIdGenerator.refresh_process_id()
        new_id = GlobalIdGenerator.PROCESS_ID
        self.assertNotEqual(old_id, new_id, "Process ID should change after refresh")

    def test_id_context(self):
        id_context = GlobalIdGenerator.IDContext(time.time_ns() // 1_000_000, 0)
        old_id = id_context.next_seq()
        new_id = id_context.next_seq()
        self.assertNotEqual(old_id, new_id, "IDContext should generate different sequences")

    def test_generate(self):
        old_id = GlobalIdGenerator.generate()
        new_id = GlobalIdGenerator.generate()
        self.assertNotEqual(old_id, new_id, "GlobalIdGenerator should generate different IDs")

    def test_id(self):
        id_obj = ID()
        self.assertIsInstance(id_obj.value, str, "ID should contain a string value")
        self.assertEqual(id_obj.value, str(id_obj), "__str__ should return the ID value")

    def test_multiprocessing_behavior(self):
        # create a separate process to test refresh_process_id
        # it will call os.fork() to create a child process in linux
        os.register_at_fork(after_in_child=GlobalIdGenerator.refresh_process_id)
        def worker(q):
            q.put(GlobalIdGenerator.PROCESS_ID)

        q = multiprocessing.Queue()
        p = multiprocessing.Process(target=worker, args=(q,))
        p.start()
        p.join()

        process_id_in_child_process = q.get()

        self.assertNotEqual(process_id_in_child_process, GlobalIdGenerator.PROCESS_ID,
                            "Process ID should change in child process after fork")

    @unittest.skipIf(not hasattr(os, 'fork'), "os.fork is not available on this system")
    def test_fork_behavior(self):
        parent_id = GlobalIdGenerator.PROCESS_ID
        os.register_at_fork(after_in_child=GlobalIdGenerator.refresh_process_id)

        newpid = os.fork()
        if newpid == 0:
            # This is the child process.
            child_id = GlobalIdGenerator.PROCESS_ID
            assert parent_id != child_id
            os._exit(0)  # It's important to terminate the child process!
        else:
            # This is the parent process.
            # Wait for the child process to exit.
            os.waitpid(newpid, 0)


if __name__ == "__main__":
    unittest.main()
