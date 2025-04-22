# Repository.py
import json
import os
import pandas

from FileManager import copy_file, delete_file, list_files_in_folder, create_new_file_in_folder, \
    create_new_folder_in_path, is_empty_folder, write_to_data_csv, read_1_row_from_data_csv, print_all_data_csv, \
    is_empty_data_csv, last_hash_code_data_csv, is_valid_path
from Commit import Commit


def init_repo(path):
    try:
        create_new_folder_in_path(os.path.join(path, ".wit"))
        create_new_folder_in_path(os.path.join(path, ".wit", "committed"))
        create_new_folder_in_path(os.path.join(path, ".wit", "staging"))
        print(f"Initialized empty Wit repository in {path}/.wit/")
    except FileExistsError:
        # If a folder wit exists
        print(f"Reinitialized existing Wit repository in {path}.wit\\")


def add_repo(path, file_name):
    # אם לא עשו עדיין Init
    if did_not_already_init(path):
        return
    # אם לא קיים כזה קובץ בתקייה
    if os.path.exists(os.path.join(path, file_name)):
        copy_file(os.path.join(path, file_name), os.path.join(path, ".wit", "staging"), )
        print(f"{file_name} file added successfully")
    else:
        print(f"fatal: pathspec '${file_name}' did not match any files")


def commit_repo(path, message):
    # אם לא עשו עדיין Init
    if did_not_already_init(path):
        return
    wit_path = os.path.join(path, ".wit")
    # בדיקה אם יש צורך בקומיט
    if is_empty_folder(os.path.join(wit_path, "staging")):
        print("There is no need to commit until you have made an addition.")
        return
    # יצירת גרסה
    commit = Commit(message)
    # יצירת תקייה לגרסה החדשה
    if os.path.exists(os.path.join(wit_path, "data.csv")):
        names = pandas.read_csv(os.path.join(wit_path, "data.csv")).iloc[:, 1]
        if message in names.values:
            print(f"A commit with that name already exists    {path}.wit\\")
            return
    try:
        create_new_folder_in_path(os.path.join(os.path.join(wit_path, "committed"), commit.hash_code))
    except FileExistsError:
        print(f"A commit with that name already exists    {path}.wit\\")
        return
    # העתקת הקבצים מה stage לגרסה החדשה
    # אם הקומיט בפעם הראשונה מכניסים את כל הקבצים שבפרויקט
    copy_from_path = path
    if os.path.exists(os.path.join(wit_path, "data.csv")):
        copy_from_path = os.path.join(wit_path, "committed", last_hash_code_data_csv(path))
    all_file_to_copy = list_files_in_folder(copy_from_path)
    # רשימת הקבצים שקיימים ב stage_path
    list_files_in_stage = list_files_in_folder(os.path.join(wit_path, "staging"))
    if all_file_to_copy is not None:
        for f in all_file_to_copy:
            if f not in list_files_in_stage:
                copy_file(os.path.join(copy_from_path, f), os.path.join(wit_path, "committed", commit.hash_code))
    for file in list_files_in_stage:
        # העתקה מהסטיגינג
        copy_file(os.path.join(wit_path, "staging", file),
                  os.path.join(wit_path, "committed", commit.hash_code))
        # ניקוי הסטיגינג
        delete_file(os.path.join(wit_path, "staging", file))
    # להכניס לקובץ הנתונים
    write_to_data_csv(path, commit)
    print(
        f" {len(list_files_in_stage)} file changed, {len(all_file_to_copy) - len(list_files_in_stage)} insertions(+), \n create new commit.\n id: {commit.hash_code}  {list_files_in_stage}")


def log_repo(path):
    # אם לא עשו עדיין Init
    if did_not_already_init(path):
        return
    print_all_data_csv(path)


def status_repo(path):
    # אם לא עשו עדיין Init
    if did_not_already_init(path):
        return
    # קבלת רשימת הקבצים ב stage_path, אם התקייה ריקה מחזיר שקר
    if is_empty_folder(os.path.join(path, ".wit", "staging")):
        print("No need to commit")
        return
    print("A commit is required.")


def checkout_repo(path, version_hash_code):
    # אם לא עשו עדיין Init
    if did_not_already_init(path):
        return
    # אם אין כזאת גרסה
    if not is_valid_path(os.path.join(path, ".wit", "committed", version_hash_code)):
        print(f"error: path spec $'{version_hash_code}' did not match any file(s) known to wit")
        return
    # עדכון הפרויקט מהגרסה
    files = list_files_in_folder(os.path.join(path, ".wit", "committed", version_hash_code))
    for f in files:
        copy_file(os.path.join(path, ".wit", "committed", version_hash_code, f), path)
    print(f"Note: switching to {version_hash_code}.")


def did_not_already_init(path):
    if not os.path.exists(os.path.join(path, ".wit")):
        print("fatal: not a wit repository (or any of the parent directories): .wit")
        return True
    return False
