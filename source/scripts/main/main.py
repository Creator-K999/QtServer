from gc import disable

from main_class import MainClass
from management.objects.objects_manager import ObjectsManager


def main():
    disable()

    main_object = ObjectsManager.create_object(MainClass)
    main_object.run()

    ObjectsManager.delete_object("MainClass")
    ObjectsManager.destruct_objects()


if __name__ == "__main__":
    main()
