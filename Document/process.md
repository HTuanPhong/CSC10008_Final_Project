# API cho hàm Download, Upload

## Upload
### Simple Upload
```python
def uploadFile(server_address, client_path, server_path):
    #server_address: tuple gồm IP và Port của server
    #client_path: đường dẫn của file cần upload trên máy client
    #server_path: đường dẫn folder đích đến cần tới bên server
```
Hàm dùng cho việc Upload file lên server, hiện tại chỉ mới cài đặt cơ bản cho việc baseline kịp tiến độ bên UI.
Chưa hỗ trợ theo dỗi tiến độ upload, tạm dừng upload, upload nhiều file(upload folder)

Dự định sẽ có class để hỗ trợ theo dõi tiến độ upload file, queue các tiến trình upload file
#### Tiến trình thực hiện
- Kiểm tra đường dẫn bên client

- Gửi yêu cầu gửi file lên server, server kiểm tra đường dẫn đích đến bên server

- Đa luồng, chia file và gửi data lên server bằng nhiều socket

- Gửi xác nhận hoàn thành việc upload lên server

#### Các Exception có thể raise và cần handle:

```python
'Lỗi không tìm thấy file bằng đường dẫn trên máy client, lỗi do Dev'
if not os.path.exists(client_path):
    raise FileNotFoundError('cant find file to upload')

'Lỗi chưa cài đặt, tính năng chưa hỗ trợ'
if os.path.isdir(client_path):
    raise NotImplementedError('chua cai :v')

'Lỗi trả về từ server'
raise error(err_msg)
    "path dont exist.",  
    # Không tìm thấy file/folder bên server, thường là lỗi Dev
    "file already uploading.",  
    # File đang Upload, khả năng cao lỗi kết nối
    "server diskspace full.",  
    # Server hết bộ nhớ, để người dùng quyết định
```

## Download
### Simple Download
```python
def downloadHelper(server_address, server_path, file_path, offset, length):
    #server_address: tuple gồm IP và Port của server
    #server_path: đường dẫn file cần download bên server
    #client_path: đường dẫn folder đích đến trên máy client
```
Hàm download baseline cơ bản, giống như upload, chưa hỗ trợ download folder, 
tạm dừng download, queue download, theo dõi tiến độ download

Về sau dự định sẽ thêm class để hỗ trợ các tính năng trên

#### Tiến trình thực hiện
- Kiểm tra đường dẫn bên client, xem đường dẫn có tồn tại hay đường dẫn có phải là folder không

- Gửi yêu cầu download file lên server, server trả về kích thước file

- Đa luồng, chia file cần download ra thành nhiều đoạn và gửi về bằng nhiều socket

- Gửi xác nhận kết thúc việc download lên server
#### Các Exception có thể raise
```python
'Lỗi không tìm thấy file bằng đường dẫn trên máy client, lỗi do Dev'
if(not os.path.exists(client_path)):
    raise FileNotFoundError('path not found')

'Lỗi đường dẫn không phải folder, lỗi do Dev'
if not os.path.isdir(client_path):
    raise OSError('not folder path')

'Lỗi do tồn tại file trùng tên trên máy, người dùng quyết định'
if os.path.exists(file_path):   #file already exist on client, user decide
    raise FileExistsError('file already exist')

'Lỗi do máy người dùng hết bộ nhớ, người dùng quyết định'
if shutil.disk_usage(client_path)[2] < file_size:
    raise OSError('server diskspace full')

'Lỗi trả về từ server'
raise error(err_msg)
    "path dont exist.",
    #Server không tìm thấy file
```