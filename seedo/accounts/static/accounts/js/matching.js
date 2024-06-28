var addPartnerBtn = document.getElementById("addPartnerBtn");
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

removePartnerBtn.addEventListener("click", function () {
  var selectedPartners = document.querySelectorAll(
    'input[name="selectPartner"]:checked',
  );
  selectedPartners.forEach((partner) => {
    partner.parentNode.remove();
  });
});

partnerList.addEventListener("click", function (event) {
  if (event.target.classList.contains("acceptBtn")) {
    var requestID = event.target.getAttribute("data-request-id");
    verifyRequestModal.style.display = "block";
    verifyRequestForm.setAttribute(
      "action",
      "/matching/accept_request/" + requestID + "/",
    );
  }
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

          // 요청 보내기
          li.onclick = function (event) {
            event.preventDefault();
            var email = user.email;
            fetch("/matching/send_request/", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
              },
              body: JSON.stringify({ email: email }),
            })
              .then((response) => response.json())
              .then((data) => {
                if (data.status === "success") {
                  alert("요청이 성공적으로 보내졌습니다.");
                  addPartnerModal.style.display = "none";
                  console.log("success");
                } else {
                  // 오류 메시지에 따라 다른 알림을 표시
                  if (data.message === "이미 요청을 보냈습니다.") {
                    alert("이미 요청을 보냈습니다.");
                  } else if (
                    data.message === "자신에게 요청을 보낼 수 없습니다."
                  ) {
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

// 수락하기 버튼 클릭 시
verifyRequestForm.addEventListener("submit", function (event) {
  event.preventDefault();
  var verificationCode = document
    .getElementById("verificationCode")
    .value.trim();
  fetch(this.getAttribute("action"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    body: JSON.stringify({ verification_code: verificationCode }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        alert("수락이 완료되었습니다.");
        verifyRequestModal.style.display = "none";
        console.log("success");

        // 수락 후 시설, 사고 버튼 표시
        var partnerName = document.querySelector(
          '.partnerName[data-request-id="' + requestID + '"]',
        );
        var pBreakLog = document.createElement("a");
        pBreakLog.href = "#";
        pBreakLog.textContent = "시설";
        pBreakLog.className = "pBreakLog";
        partnerName.parentNode.insertBefore(pBreakLog, partnerName.nextSibling);
        var pAccidentLog = document.createElement("a");
        pAccidentLog.href = "#";
        pAccidentLog.textContent = "사고";
        pAccidentLog.className = "pAccidentLog";
        partnerName.parentNode.insertBefore(
          pAccidentLog,
          partnerName.nextSibling,
        );
      } else {
        alert("수락하는 도중 오류가 발생했습니다.");
        console.error(data.errors);
      }
    });
});
