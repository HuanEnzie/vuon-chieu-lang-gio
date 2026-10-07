# Vườn Chiều Lặng Gió — phim 60 giây

Phim hoạt hình 60 giây dựng hoàn toàn bằng code từ chính khu vườn voxel của trang web (Three.js + shader hậu kỳ), render bằng [HyperFrames](https://hyperframes.heygen.com). Không dùng model AI tạo video.

- `src/film.tpl.html` — kịch bản phim: 8 cảnh camera, lịch trình của chủ vườn, cún, mèo, gà, thỏ, cá; mọi chuyển động là hàm thuần của thời gian nên render từng khung hình độc lập.
- `build_video.py` — lấy thế giới, nhân vật và shader từ `../vuon-chieu.src.html`, chèn phụ đề và texture, trộn nhạc Mixkit thành `assets/audio/soundtrack.wav`, xuất `index.html`.
- `vuon-chieu-60s.mp4` — bản nén để xem nhanh.

Dựng lại:

```bash
npm i
python build_video.py
npx hyperframes render --fps 24 -o renders/vuon-chieu-60s.mp4
```

Nguồn âm thanh: xem `CREDITS.md`.
