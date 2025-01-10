# AutoBuilding the training parallel corpus for Chinese OCR by crawling + aligning images and texts

Ngữ liệu của chúng em được xây dựng từ PDF chứa ảnh 50 chương đầu tiên của văn bản "Tây Du Ký". Ngữ liệu này bao gồm khoảng 14,000 dòng chữ Hán được OCR từ bản PDF và được dóng hàng với độ chính xác mức ký tự với nội dung văn bản của Tây Du Ký lấy từ website gutenberg.org.

## **1. Thu thập và xử lý dữ liệu từ Web**
Trước khi thực hiện dóng hàng, ta cần thu thập văn bản sẽ được dùng để làm chuẩn cho việc so sánh. Đối với Tây Du Ký, ta sẽ lấy về nội dung văn bản thông qua trang web gutenberg.org với các bước như sau:
1. Ta truy cập url của trang web và lấy về toàn bộ nội dung HTML.
2. Ta trích nội dung từ các đoạn văn bản (<p> trong HTML) và lưu về tập tin raw_text.txt.
3. Từ raw_text.txt, ta làm sạch văn bản bằng cách loại các kí tự không thuộc nội dung gốc (kí tự xuống hàng, dấu cách, v.v).
4. Sau khi làm sạch văn bản, ta lưu nội dung vào tập tin clean_text.txt.

## **2. Trích xuất hình ảnh và văn bản từ PDF**
Trước tiên, ta sẽ cần trích xuất hình ảnh các trang của PDF qua các bước sau:
1. Trích xuất ảnh từ trang PDF hiện tại bằng thư viện fitz.
2. Sử dụng thư viện Image của PIL, ta thực hiện nâng chất lượng của ảnh (để hỗ trợ việc OCR) và lưu ảnh với tên file là số trang ("page_{num}.png").
3. Trong code, tạo vòng lặp để lặp lại 2 bước trên với tất cả các trang PDF.

Sau khi đã có được ảnh, ta sẽ cần lấy nội dung văn bản từ các ảnh đó. Để lấy được văn bản, ta sẽ dùng API của KandianGuji để OCR văn bản và thực hiện các bước sau:
1. Đổi ảnh cần OCR về dạng chuỗi ký tự Base64 để đưa vào tham số khi gọi API.
2. Ta gọi API với các tham số cần thiết và lưu kết quả phản hồi là một tập tin json ("TayDuKy_page_{num}.json").
3. Trong code, tạo vòng lặp để lặp lại 2 bước trên với tất cả các ảnh đã trích xuất được.

## **3. Thực hiện đóng hàng câu và chữ**
Sau khi có được kết quả OCR, ta thực hiện đóng hàng các chuỗi OCR với văn bản chuẩn bằng cách đi tìm chuỗi chữ trong clean_text.txt giống nhất với chuỗi OCR đang so sánh. Quy trình đóng hàng câu được thực hiện
như sau:
1. Với chuỗi OCR đang xét, đi qua từng chuỗi con có độ dài tương tự trong clean_text.txt và tính độ giống nhau.
2. Tính điểm số so khớp giữa chuỗi OCR và từng chuỗi con bằng cách sử dụng thuật toán SequenceMatcher từ thư viện difflib. Điểm số được tính bằng tổng số ký tự giống nhau chia cho độ dài của chuỗi OCR.
3. Lưu lại chuỗi con với độ giống cao nhất.
4. Kiểm tra xem độ giống nhau cao nhất có vượt quá ngưỡng 0.35 hay không. Nếu có, thêm cặp OCR box đang xét và chuỗi con giống nhất vào danh sách kết quả.
5. Với vị trí bắt đầu mới nằm sau chuỗi con vừa tìm được, ta quay lại bước 1 và tiếp tục đóng hàng các chuỗi OCR cho đến khi hết chuỗi.
6. Từ danh sách kết quả đóng hàng, ta xuất ra một tập tin json để lưu các chuỗi OCR, các chuỗi văn bản chuẩn và các thông tin cần thiết (số thứ tự OCR box, số thứ tự trang, v.v).

Từ tập tin json đó, ta bắt đầu đóng hàng chữ giữa các chuỗi như sau:
1. Với mỗi cặp chuỗi, thực hiện thuật toán MED để đóng hàng các chữ và chú thích quan hệ giữa các cặp chữ (ví dụ: giống nhau, khác nhau, v.v.).
2. Thực hiện đóng hàng chữ với tất cả các cặp chuỗi và lưu kết quả vào align_text.json.

### **3.1. Điều kiện kiểm tra sự giống nhau của hai câu**
Để xác định hai câu OCR và văn bản chuẩn có giống nhau hay không, chúng ta áp dụng các điều kiện sau:
1. Chuyển đổi ký tự Hán tự đơn giản hóa: Trước khi so sánh, các chuỗi ký tự Hán tự của cả hai nguồn (OCR và văn bản chuẩn) được chuyển đổi sang dạng đơn giản hóa bằng hàm convert_hanzi_strings. Điều này giúp giảm thiểu sự khác biệt về dạng chữ viết.
2. Tính điểm số so khớp: Sử dụng thuật toán SequenceMatcher để xác định các khối ký tự giống nhau giữa hai chuỗi. Điểm số so khớp được tính bằng tỷ lệ số ký tự giống nhau so với độ dài của chuỗi OCR. Công thức tính điểm số: $$\text{score} = \displaystyle \frac{\text{matching chars}}{\text{len(ocr text)}}$$

Nếu độ giống nhau vượt qua ngưỡng tối thiểu là 0.35, hai câu được xem là giống nhau.
3. Xác định vị trí khớp: Sau khi xác định được chuỗi con giống nhất, ta tìm vị trí bắt đầu của các ký tự giống nhau trong cả hai chuỗi bằng cách sử dụng hàm align_strings. Nếu không tìm được vị trí khớp, chuỗi OCR hiện tại sẽ không được đóng hàng và quá trình tiếp tục với chuỗi tiếp theo.
4. Cắt chuỗi văn bản chuẩn: Nếu điểm số so khớp đủ cao, ta cắt phần chuỗi văn bản chuẩn tương ứng với chuỗi OCR để đảm bảo rằng các phần tiếp theo không bị trùng lặp khi tiếp tục đóng hàng.
### **3.2. Xuất kết quả dóng hàng**
Sau khi hoàn tất quá trình đóng hàng, ta thực hiện xuất kết quả dưới các định dạng sau:
1. Tập tin JSON: Chứa các thông tin về các hộp OCR, văn bản gốc và các thông tin bổ sung như số thứ tự OCR box, số thứ tự trang, vị trí trong trang, v.v. Điều này giúp dễ dàng truy xuất và xử lý dữ liệu sau này.
2. Tập tin CSV: Ghi lại các cặp văn bản OCR và văn bản chuẩn đã được đóng hàng, thuận tiện cho việc kiểm tra và phân tích dữ liệu.

Nhờ vào các điều kiện và quy trình kiểm tra chặt chẽ, quá trình đóng hàng không chỉ đảm bảo độ chính xác cao mà còn tối ưu hiệu suất xử lý dữ liệu OCR

Sau khi đã dóng hàng chữ, ta sẽ dùng hàm write_output.py để thực hiện đọc file align_text.json và xuất ra tập tin Excel:
![image](https://github.com/user-attachments/assets/d00c2202-99b4-444b-b0d2-0a3f9132c768)
