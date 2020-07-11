from limberframework.support.metaclasses import Singleton

def test_singleton():
    class TestSingleton(metaclass=Singleton):
        pass

    test_singleton_1 = TestSingleton()
    test_singleton_2 = TestSingleton()

    assert test_singleton_1 is test_singleton_2
