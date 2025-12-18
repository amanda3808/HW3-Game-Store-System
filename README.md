- 操作流程:
1. 修改程式 server HOST (現在是"140.113.17.11")
2. server端 $ python3 server/server.py
- - 確保目錄有w權限不然建不了db.json $ chmod -R u+rwX 目錄
3. developer端 $ python3 developer/developer.py
4. 註冊、登入、上架、更新遊戲
- - 選項有顯示bug，看起來預設全選但其實並沒有，要用滑鼠點一次
- - 無論是否下架，所有上架、更新所上傳的檔案名稱不能相同
- - gclient.py、gserver.py是一個猜數字的3人遊戲，最好不要把它覆蓋掉不然重新上傳要改名字，有其他檔案可以測試
5. player端 $ python3 player/player.py，猜數字遊戲需要3人
6. 註冊、登入、選擇遊戲、下載、建立房間、加入房間、開始遊戲、結束、評論、並回到大廳
- - 選項有顯示bug，看起來預設全選但其實並沒有，要用滑鼠點一次