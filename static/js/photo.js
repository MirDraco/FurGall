const accordionHeaders = document.querySelectorAll(".accordion-header");
// 아코디언 토글 기능
document.querySelectorAll(".accordion-header").forEach((button) => {
  button.addEventListener("click", () => {
    const content = button.nextElementSibling;
    const icon = button.querySelector(".icon");

    // 토글 활성화
    button.classList.toggle("active");
    content.classList.toggle("active");

    // 열릴 때마다 사진 로드 (최신 데이터 반영)
    if (content.classList.contains("active")) {
      // 버튼 텍스트에서 숫자만 추출 (공백, 특수문자 제거)
      const year = button.textContent.replace(/\D/g, "").trim();
      console.log(`🟡 추출된 연도: "${year}"`);
      loadPhotos(year, content);
    }
  });
});

// 특정 연도의 사진 불러오기
async function loadPhotos(year, container) {
  try {
    console.log(`📸 ${year}년 사진 로딩 시작...`);

    // 로딩 표시
    container.innerHTML = '<p style="color: white; grid-column: 1/-1; text-align: center;">로딩 중...</p>';

    // Flask API 호출
    const url = `/api/photos/${year}`;
    console.log("🔵 요청 URL:", url);
    const response = await fetch(url);
    console.log("🔵 응답 상태:", response.status);
    console.log("🔵 응답 객체:", response);

    const photos = await response.json();
    console.log("🔵 받은 데이터:", photos);
    console.log("🔵 데이터 타입:", typeof photos);
    console.log("🔵 데이터 길이:", photos.length);

    // 사진이 없으면
    if (photos.length === 0) {
      container.innerHTML =
        '<p style="color: white; grid-column: 1/-1; text-align: center;">아직 업로드된 사진이 없습니다.</p>';
      return;
    }

    // 기존 내용 제거
    container.innerHTML = "";

    // 각 사진을 img 태그로 추가 (삭제 버튼 포함)
    photos.forEach((photo) => {
      // 사진 아이템 컨테이너 생성
      const photoItem = document.createElement("div");
      photoItem.className = "photo-item";
      photoItem.dataset.filename = photo.filename;

      // 이미지 생성
      const img = document.createElement("img");
      img.src = photo.url;
      img.alt = photo.filename;
      img.className = "photo-img";
      img.loading = "lazy";

      img.addEventListener("click", () => {
        window.open(photo.url, "_blank");
      });

      // 삭제 버튼 생성
      const deleteBtn = document.createElement("button");
      deleteBtn.className = "delete-btn";
      deleteBtn.innerHTML = "🗑️";
      deleteBtn.onclick = (e) => {
        e.stopPropagation(); // 이미지 클릭 이벤트와 겹치지 않게
        deletePhoto(year, photo.filename);
      };

      // 컨테이너에 이미지와 버튼 추가
      photoItem.appendChild(img);
      photoItem.appendChild(deleteBtn);
      container.appendChild(photoItem);
    });

    console.log(`✅ ${year}년 사진 ${photos.length}개 로드 완료`);
  } catch (error) {
    console.error("❌ 사진 로딩 실패:", error);
    container.innerHTML =
      '<p style="color: white; grid-column: 1/-1; text-align: center;">❌ 사진을 불러오는데 실패했습니다.</p>';
  }
}

// 삭제 함수
function deletePhoto(year, filename) {
  if (!confirm("정말 삭제하시겠습니까?")) return;

  fetch(`/api/photos/${year}/${filename}`, {
    method: "DELETE",
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("삭제되었습니다");
        // 해당 사진만 DOM에서 제거
        document.querySelector(`[data-filename="${filename}"]`).remove();
      } else {
        alert("삭제 실패: " + data.error);
      }
    })
    .catch((error) => {
      console.error("삭제 오류:", error);
      alert("삭제 중 오류가 발생했습니다");
    });
}
