# Chương trình download/upload file client-server dùng kỹ thuật đa luồng

Một chương trình download/upload file đa luồng yêu cầu client và server có khả năng truyền nhận dữ liệu file một cách đa luồng, ở đây client là bên gửi yêu cầu đầu tiên và server là bên cung cấp phản hồi.

Tuy nhiên để dễ dàng trong lúc sử dụng ta có thể thêm một số chức năng như tạo folder, xóa file, xóa folder, truyền thông tin các file hiện có.

## Giao thức quản lý tập tin cơ bản

Tất nhiên để client và server có những khả năng trên thì server cần hiểu yêu cầu từ client và client hiểu phản hồi từ server. Vì vậy ở đây chúng ta sẽ định nghĩa một giao thức quản lý tập tin cơ bản.

### Sơ lược về giao thức

Giao thức mà chúng ta định nghĩa sau đây sẽ sử dụng giao thức TCP ở tầng transport. Cách gửi và yêu cầu 1 đoạn dữ liệu đã được tham khảo từ chức năng [Byte serving](https://en.wikipedia.org/wiki/Byte_serving) của giao thức [HTTP](https://en.wikipedia.org/wiki/HTTP) sẽ cho phép ta lập trình đa luồng dễ dàng hơn. Cách phân biệt mã lệnh bằng opcode được tham khảo từ giao thức [TFTP](https://datatracker.ietf.org/doc/html/rfc1350#autoid-5) (vì nó đơn giản) và cuối cùng cách đồng bộ hóa dữ liệu sẽ dùng cách giao tiếp [Push technology](https://en.wikipedia.org/wiki/Push_technology) thông qua một quá trình được gọi là [publish–subscribe model](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern) nhằm giảm lượng dữ liệu trên đường truyền.

### Quy ước mã lệnh

Ở đây ta sẽ liệt kê các mệnh lệnh mà client có thể yêu cầu từ server:

| opcode | tên gọi                     |
|:------:|-----------------------------|
|    0   | Read request (RRQ)          |
|    1   | Write request (WRQ)         |
|    2   | Data read request (DRRQ)    |
|    3   | Data write request (DWRQ)   |
|    4   | Finish write request (FWRQ) |
|    5   | Delete request (DRQ)        |
|    6   | Directory request (DTRQ)    |
|    7   | Create folder request (FRQ) |

và kết quả client nhận từ server:

| opcode | tên gọi           |
|:------:|-------------------|
|    0   | Error (ERROR)     |
|    1   | Success (SUCCESS) |

### Quy ước chung của các lệnh

- Kích cỡ địa chỉ tối đa là 2^8 bytes = 255 bytes.
- Kích cỡ file tối đa là 2^(8*8) bytes ~ 18.3 exabytes.
- Khi một đoạn gửi đi từ client đến server có độ dài n bytes thì đoạn đứng trước mang giá trị số cho n.
- Server sẽ gửi cấu trúc giống nhau khi có lỗi.
- Số sẽ được gửi theo kiểu [Big endian](https://en.wikipedia.org/wiki/Endianness), chuỗi ký tự (string) được gửi theo định dạng [UTF-8](https://en.wikipedia.org/wiki/UTF-8)

### Trường hợp server báo lỗi

![Error](./diagrams/Error.svg)

Ta đi vào trường hợp lỗi đầu tiên vì đây là cấu trúc sẽ được dùng cho mọi trường hợp lỗi server gửi về. Bất kể dữ liệu gửi đi server sẽ trả về đầu tiên là 1 byte opcode giá trị 0 nghĩa là kết quả lỗi so với bảng trên kèm theo 1 byte độ dài lỗi và n bytes ký tự thông điệp lỗi.

### Lệnh read request (RRQ)

![Read request](./diagrams/Read%20request.svg)

Đây là lệnh yêu cầu đọc file. Client sẽ gửi 1 byte số cho opcode, 1 byte số cho kích cỡ địa chỉ, cuối cùng là n bytes ký tự cho địa chỉ file trên server. Server sẽ trả lại 1 byte opcode và 8 bytes cho kích cỡ file trong database nếu không gặp lỗi. Lỗi có thể trả về ở đây là khi địa chỉ không hợp lệ.

### Lệnh write request (WRQ)

![Write request](./diagrams/Write%20request.svg)

Đây là lệnh yêu cầu ghi file. Client sẽ gửi 1 byte số cho opcode, 1 byte số cho kích cỡ địa chỉ, n bytes ký tự cho địa chỉ file, cuối cùng là 8 bytes số cho kính cỡ file. Server sẽ tạo một file trong database với kích cỡ từ client và tên từ client đã gửi kèm ".uploading" sau đó trả lại 1 byte opcode nếu không gặp lỗi. Lỗi có thể trả về ở đây là địa chỉ không hợp lệ, server không đủ dung lượng, file đã đang được ghi (đã có file ".uploading").

### Lệnh data read request (DRRQ)

![Data read request](./diagrams/Data%20read%20request.svg)

Đây là lệnh yêu cầu đọc dữ liệu vào file. Client sẽ gửi 1 byte số cho opcode, 1 byte số cho kích cỡ địa chỉ, n bytes ký tự cho địa chỉ file, 8 bytes số cho vị trí đọc dữ liệu, 8 bytes số cho độ dài dữ liệu cần đọc. Server sẽ gửi về 1 byte opcode, n bytes đoạn dữ liệu của file tại vị trí client yêu cầu nếu không gặp lỗi. Lỗi có thể trả về ở đây là địa chỉ không hợp lệ, vị trí đọc không hợp lệ, độ dài đọc không hợp lệ.

### Lệnh data write request (DWRQ)

![Data write request](./diagrams/Data%20write%20request.svg)

Đây là lệnh yêu cầu ghi dữ liệu vào file. Client sẽ gửi 1 byte số cho opcode, 1 byte số cho kích cỡ địa chỉ, n bytes ký tự cho địa chỉ file, 8 bytes số cho vị trí ghi dữ liệu, 8 bytes số cho độ dài dữ liệu cần ghi, n bytes cho đoạn dữ liệu. Server sẽ ghi đoạn dữ liệu nhận được vào vị trí trong file ".uploading" client yều cầu sau đó gửi về 1 byte opcode nếu không gặp lỗi. Lỗi có thể trả về ở đây là địa chỉ không hợp lệ, vị trí ghi không hợp lệ, độ dài ghi không hợp lệ.

### Lệnh finish write request (FWRQ)

![Finish write request](./diagrams/Finish%20write%20request.svg)

Đây là lệnh hoàn thành quá trình ghi file. Client sẽ gửi 1 byte số cho opcode, 1 byte số cho kích cỡ địa chỉ, n bytes ký tự cho địa chỉ file. Server sẽ cắt bỏ phần ".uploading" và file coi như sẽ không được ghi nữa sau đó gửi về 1 byte opcode nếu không gặp lỗi. Lỗi có thể trả về ở đây là địa chỉ không hợp lệ.

### Lệnh delete request (DRQ)

![Delete request](./diagrams/Delete%20request.svg)

Đây là lệnh yêu cầu xóa file/folder. Client sẽ gửi 1 byte số cho opcode, 1 byte số cho kích cỡ địa chỉ, n bytes ký tự cho địa chỉ file/folder. Server sẽ xóa file/folder tại địa chỉ client yều cầu và trả về 1 byte opcode nếu không gặp lỗi. Lệnh này không có lỗi trả về.

### Lệnh directory request (DTRQ)

![Directory request](./diagrams/Directory%20request.svg)

Đây là lệnh đồng bộ hóa dữ liệu thông qua mô hình [publish–subscribe](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern). Client sẽ gửi 1 byte opcode nhằm đang ký (subcribe) kết nối hiện tại cho quá trình đồng bộ. Server sẽ gửi ngay lặp tức 1 byte opcode, 4 bytes cho độ dài dữ liệu, n bytes dữ liệu database định dạng [JSON](https://en.wikipedia.org/wiki/JSON) sau khi client gửi opcode, sau đó kết nối này vẫn giữ nguyên trạng thái và mỗi khi database có thay đổi server sẽ tự động xuất bản (publish) dữ liệu như trên về client mà không cần yêu cầu từ client nếu kết nối TCP vẫn được mở. Lệnh này không có lỗi trả về.

### Lệnh create folder request (FRQ)

![Create folder request](./diagrams/Create%20folder%20request.svg)

Đây là lệnh tạo folder. Client sẽ gửi 1 byte số cho opcode, 1 byte số cho kích cỡ địa chỉ, n bytes ký tự cho địa chỉ folder. Server sẽ tạo folder với địa chỉ client yêu cầu và gửi 1 byte opcode nếu không gặp lỗi. Lỗi có thể trả về ở đây là địa chỉ không hợp lệ, không thể tạo folder.

## Sử dụng giao thức quản lý tập tin cơ bản

Với những lệnh đã có ở trên ta sẽ dễ dàng lập trình hệ thống download/upload file client-server dùng kỹ thuật đa luồng.

### Quy trình đồng bộ dữ liệu

![Sync directory](./diagrams/Sync%20directory.svg)

Chức năng này không cần thiết đối với một quá trình download/upload thông thường dùng giao thức mà ta đã định nghĩa nhưng đối với chương trình dùng để quản lý tập tin thư mục thì chức năng này là cần thiết và vì hầu hết chương trình có chức năng download/upload hiện nay là để quản lý tập tin thư mục nên chúng ta sẽ thêm vào chương trình chức năng này.

### Quy trình upload file lên server

![Upload](./diagrams/Upload.svg)

Để upload file lên server, client cần biết địa chỉ trong database muốn đặt file vào địa chỉ này có thể được quy ước, được định sẵn hoặc được biết từ quá trình đồng bộ dữ liệu. Quá trình ghi dữ liệu vào file là bước mà ta có thể sử dụng kỹ thuật đa luồng chia file và gửi từng đoạn riêng biệt qua nhiều kết nối tất nhiên quá trình này hoàn toàn có thể chạy trên 1 luồng tùy nhu cầu người dùng. Việc gửi lệnh hoàn thành quá trình ghi là cần thiết để server biết file này sẽ không còn được ghi trong tương lai. Trong chương trình ta sẽ lấy địa chỉ từ quá trình đồng bộ dữ liệu và số luồng mặc định là 8 đây là con số ngẫu nhiên và không có ý nghĩa sâu xa gì.

### Quy trình download file xuống client

![Download](./diagrams/Download.svg)

Để download file xuống client, client cần biết địa chỉ và kích thước file trên server, địa chỉ này có thể được quy ước, được định sẵn hoặc được biết từ quá trình đồng bộ dữ liệu, kích thước file có thể được lấy từ lệnh read request hoặc quá trình đồng bộ dữ liệu. Quá trình đọc dữ liệu vào file là bước mà ta có thể sử dụng kỹ thuật đa luồng đọc từng đoạn riêng biệt qua nhiều kết nối tất nhiên quá trình này hoàn toàn có thể chạy trên 1 luồng tùy nhu cầu người dùng. Trong chương trình ta sẽ lấy địa chỉ và kích thước từ quá trình đồng bộ dữ liệu nên không cần lệnh read request và số luồng mặc định là 8 đây là con số ngẫu nhiên và không có ý nghĩa sâu xa gì.

### Một số quy trình đơn giản

Để xóa file/folder, tạo folder là những quy trình đơn giản chỉ cần gọi đúng lệnh tương ứng.

Quy trình upload folder là sự kết hợp giữa quy trình tạo folder và upload file.

## Cấu trúc code của chương trình

![Code structure](./diagrams/Code%20structure.svg)

Để thực hiện việc giao tiếp giữa Client và Server, Client sẽ có modules là Message.py bao gồm những hàm và thủ tục giúp ứng dụng bên Client đóng gói những yêu cầu, dữ liệu cần gửi cũng như là giúp nhận dạng thông điệp phản hồi từ Server. Những thông điệp từ Server giúp báo hiệu là yêu cầu đã được xử lí hay là đã xảy ra lỗi. Đối với Server sẽ có modules là request.py giúp xử lí các yêu cầu gửi từ client. Việc xử lí các yêu cầu bao gồm việc kiểm lỗi, gửi lại thông điệp phản hồi cho Client.

Giao thức được định nghĩa ở trên sẽ được lập trình vào Message.py và Request.py .

Giao diện người dùng sẽ được lập trình vào Client.py và Server.py .