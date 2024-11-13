import json
from lib import (
    connect_db, create_table, import_movies, search_movies,
    add_movie, modify_movie, delete_movies, export_movies
)

DB_PATH = "movies.db"
JSON_IN_PATH = "movies.json"
JSON_OUT_PATH = "exported.json"

def main():
    conn = connect_db(DB_PATH)
    create_table(conn)

    while True:
        print("\n----- 電影管理系統 -----")
        print("1. 匯入電影資料檔")
        print("2. 查詢電影")
        print("3. 新增電影")
        print("4. 修改電影")
        print("5. 刪除電影")
        print("6. 匯出電影")
        print("7. 離開系統")
        print("------------------------")
        
        choice = input("請選擇操作選項 (1-7): ")
        if choice == '1':
            import_movies(conn, JSON_IN_PATH)
        elif choice == '2':
            search_movies(conn)
        elif choice == '3':
            add_movie(conn)
        elif choice == '4':
            modify_movie(conn)
        elif choice == '5':
            delete_movies(conn)
        elif choice == '6':
            export_movies(conn, JSON_OUT_PATH)
        elif choice == '7':
            print("系統已退出。")
            break
        else:
            print("請輸入正確的選項！")

    conn.close()

if __name__ == "__main__":
    main()
