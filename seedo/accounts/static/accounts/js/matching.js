var addPartnerBtn = document.getElementById("addPartnerBtn");
var acceptBtn = document.getElementById("acceptBtn");
var removePartnerBtn = document.getElementById("removePartnerBtn");
var addPartnerModal = document.getElementById("addPartnerModal");
var verifyRequestModal = document.getElementById("verifyRequestModal");
var sendRequestForm = document.getElementById("sendRequestForm");
var verifyRequestForm = document.getElementById("verifyRequestForm");
var partnerList = document.querySelector(".partnerList");

// CSRF 토큰을 메타 태그에서 가져오는 함수
function getCsrfToken() {
  return document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute("content");
}

addPartnerBtn.addEventListener("click", function () {
  addPartnerModal.style.display = "block";
});
// 수락 버튼 클릭 시 모달 열기
document.querySelectorAll(".acceptBtn").forEach(function (button) {
  button.addEventListener("click", function () {
    var requestId = this.getAttribute("data-request-id");
    verifyRequestForm.setAttribute(
      "action",
      `/matching/accept_request/${requestId}/`,
    );
    verifyRequestModal.style.display = "block";
  });
});

// Close modals
var modals = document.querySelectorAll(".modal");
modals.forEach((modal) => {
  modal.addEventListener("click", function (event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
});

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}
// 이메일 검색 및 사용자 목록 표시
document.getElementById("email").addEventListener("input", function () {
  var email = this.value.trim();
  var searchResults = document.getElementById("searchResults");

  // 입력된 이메일이 있을 때만 검색 요청
  if (email.length > 0) {
    fetch("/matching/search/?email=" + email)
      .then((response) => response.json())
      .then((data) => {
        console.log(data); // 서버에서 받은 데이터 확인

        // 검색 결과를 초기화
        searchResults.innerHTML = "";

        // 받은 사용자 목록을 리스트에 추가
        data.users.forEach((user) => {
          var li = document.createElement("li");
          li.textContent = user.email;
          li.setAttribute("data-user-id", user.id);

          li.onclick = function () {
            // 이메일 입력 필드에 선택한 이메일 설정
            document.getElementById("email").value = user.email;

            // 요청 보내기 함수 호출
            sendRequest(user.email);

            searchResults.innerHTML = ""; // 목록 클릭 시 검색 결과 초기화
          };

          searchResults.appendChild(li); // 검색 결과 리스트에 추가
        });
      })
      .catch((error) => {
        console.error("Error fetching users:", error);
      });
  } else {
    searchResults.innerHTML = ""; // 입력값이 없을 때 검색 결과 초기화
  }
});

// 요청 보내기 함수
function sendRequest(email) {
  var csrftoken = getCookie("csrftoken");

  fetch("/matching/send_request/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ email: email }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        alert("요청이 성공적으로 보내졌습니다.");
        addPartnerModal.style.display = "none";
        location.reload();
      } else {
        // 오류 메시지에 따라 다른 알림을 표시
        if (data.message === "이미 요청을 보냈습니다.") {
          alert("이미 요청을 보냈습니다.");
        } else if (data.message === "자신에게 요청을 보낼 수 없습니다.") {
          alert("자신에게 요청을 보낼 수 없습니다.");
        } else {
          alert("요청을 보내는 도중 오류가 발생했습니다.");
        }
        console.error(data.message);
      }
    })
    .catch((error) => {
      alert("요청을 보내는 도중 오류가 발생했습니다.");
      console.error("Error:", error);
    });
}

// 수락하기 버튼 클릭 시
verifyRequestForm.addEventListener("submit", function (event) {
  event.preventDefault();
  var verificationCode = document
    .getElementById("verificationCode")
    .value.trim();
  var csrftoken = getCookie("csrftoken");

  fetch(this.getAttribute("action"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ verification_code: verificationCode }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        alert("수락이 완료되었습니다.");
        verifyRequestModal.style.display = "none";
        location.reload();
      } else {
        alert(data.message || "수락하는 도중 오류가 발생했습니다.");
        console.error(data.errors);
      }
    });
});
removePartnerBtn.addEventListener("click", function () {
  var selectedPartners = document.querySelectorAll(
    'input[name="selectPartner"]:checked',
  );

  selectedPartners.forEach((partner) => {
    var requestID = partner.getAttribute("data-request-id");
    var csrftoken = getCookie("csrftoken");

    if (!requestID) {
      console.error("Request ID가 null입니다.");
      return;
    }

    // DELETE 요청 보내기
    fetch(`/matching/remove_connection/${requestID}/`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
    })
      .then((response) => {
        if (response.ok) {
          partner.closest(".eachPartner").remove(); // 삭제 성공 시 DOM에서 해당 요소 삭제
          console.log("삭제 성공");
        } else {
          console.error("삭제 실패");
        }
      })
      .catch((error) => {
        console.error("오류 발생:", error);
      });
  });
});
