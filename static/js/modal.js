const uploadModal = document.getElementById("uploadModal");
const modalContent = uploadModal.querySelector(".upload-box");
const modalOverlay = uploadModal.querySelector(".modal-overlay");

function openUploadModal() {
  uploadModal.style.display = "block"; // 먼저 보이게 함
  modalContent.classList.remove("hide");
  modalContent.classList.add("show");
  modalOverlay.classList.remove("hide");
  modalOverlay.classList.add("show");
}

function closeUploadModal() {
  modalContent.classList.remove("show");
  modalContent.classList.add("hide"); // 사라지는 애니메이션 시작
  modalOverlay.classList.remove("show");
  modalOverlay.classList.add("hide");

  // 애니메이션 시간(0.3s = 300ms)이 지난 후 아예 숨김
  setTimeout(() => {
    uploadModal.style.display = "none";
  }, 300);
}
// photo.html의 JavaScript 부분

// 사진 렌더링 시 삭제 버튼 추가
function renderPhotos(photos, year) {
  const gallery = document.getElementById("photo-gallery");
  gallery.innerHTML = photos
    .map(
      (photo) => `
        <div class="photo-item" data-filename="${photo.filename}">
            <img src="${photo.url}" alt="사진">
            <button class="delete-btn" onclick="deletePhoto('${year}', '${photo.filename}')">
                🗑️
            </button>
        </div>
    `,
    )
    .join("");
}
