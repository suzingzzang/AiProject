var map;
var markers = [];
var polyline;
var currentWaypointIndex = 0;
var waypoints = [];
var routeSearchStarted = false;
var pathCoordinates = [];

let markerLatLng, infoWindow;
let startLocation, startMarker;
let endLocation, endMarker;
let currentLocation, currentMarker;

async function ttsAlert(text) {
  var csrftoken = getCookie("csrftoken");
  try {
    const response = await fetch("/nav/tts/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);

    try {
      await audio.play();
      console.log("음성 재생 성공");
    } catch (error) {
      console.error("음성 재생 중 오류 발생:", error);
    }
  } catch (error) {
    console.error("TTS 변환 중 오류 발생:", error);
  }
}

// 기존 alert 함수를 불러올때 ttsAlert 함수 호출
window.alert = function(text) {
  ttsAlert(text); // TTS 변환 함수 호출
  window.alert = ttsAlert; // alert 함수를 다시 TTS 함수로 설정하여 중복 호출 방지
};


function initMap() {
  map = new Tmapv2.Map("map", {
    center: new Tmapv2.LatLng(37.5665, 126.978),
    zoom: 13,
    httpsMode: true,
  });
  // 현재 위치 가져오기
  getCurrentLocation();

  map.addListener("click", function (event) {
    if (infoWindow) {
      infoWindow.setVisible(false);
    }

    markerLatLng = event.latLng;
    if (!routeSearchStarted) {
      var content = `<div style='width: 120px'>
                       <div onclick='addMarker("start")'>출발지 설정</div>
                       <div onclick='addMarker("end")'>목적지 설정</div>
                     </div>`;
      //Popup 객체 생성.
      infoWindow = new Tmapv2.InfoWindow({
        position: new Tmapv2.LatLng(event.latLng.lat(), event.latLng.lng()), //Popup 이 표출될 맵 좌표
        content: content, //Popup 표시될 text
        type: 2, //Popup의 type 설정.
        border: 4,
        map: map, //Popup이 표시될 맵 객체
      });
    }
  });

  map.addListener("touchstart", function (event) {
    if (infoWindow) {
      infoWindow.setVisible(false);
    }

    markerLatLng = event.latLng;
    if (!routeSearchStarted) {
      var content = `<div style='width: 120px'>
                       <div ontouchstart='addMarker("start")'>출발지 설정</div>
                       <div ontouchstart='addMarker("end")'>목적지 설정</div>
                     </div>`;
      //Popup 객체 생성.
      infoWindow = new Tmapv2.InfoWindow({
        position: new Tmapv2.LatLng(event.latLng.lat(), event.latLng.lng()), //Popup 이 표출될 맵 좌표
        content: content, //Popup 표시될 text
        type: 2, //Popup의 type 설정.
        border: 4,
        map: map, //Popup이 표시될 맵 객체
      });
    }
  });
}


function successCallback(position) {
  var lat = position.coords.latitude;
  var lng = position.coords.longitude;
  currentLocation = new Tmapv2.LatLng(lat, lng);

  // 현재 위치 마커 초기화 또는 위치 업데이트
  if (!currentMarker) {
    currentMarker = new Tmapv2.Marker({
      position: currentLocation,
      map: map, // 반드시 map 옵션을 설정하여 지도에 연결
      title: "현재 위치",
    });
  } else {
    // 기존 마커가 있을 경우 삭제하고 새로운 마커 생성
    currentMarker.setMap(null); // 기존 마커 삭제

    currentMarker = new Tmapv2.Marker({
      position: currentLocation,
      map: map,
      title: "현재 위치",
    });
  }

  map.panTo(currentLocation); // 지도를 현재 위치로 이동
}
function stopnavi(){
  localStorage.removeItem("routeData");
  window.location.reload();
  
}
function displayRoute(directionsData) {
  if (polyline) {
    polyline.setMap(null);
  }

  var features = directionsData.features;
  pathCoordinates = [];
  var points = [];
  waypoints = [];

  features.forEach(function (feature) {
    if (feature.geometry.type === "Point") {
      var pointCoordinates = feature.geometry.coordinates;
      var point = new Tmapv2.LatLng(pointCoordinates[1], pointCoordinates[0]);
      points.push(point);
      waypoints.push(point); // 안내 지점 추가
    } else if (feature.geometry.type === "LineString") {
      var lineCoordinates = feature.geometry.coordinates;
      lineCoordinates.forEach(function (coord) {
        var point = new Tmapv2.LatLng(coord[1], coord[0]);
        pathCoordinates.push(point);
      });
    }
  });

  polyline = new Tmapv2.Polyline({
    path: pathCoordinates,
    strokeColor: "#FF0000",
    strokeWeight: 3,
    map: map,
  });

  var bounds = new Tmapv2.LatLngBounds();
  points.forEach(function (point) {
    bounds.extend(point);
  });
  map.fitBounds(bounds);

  var routeInfoContainer = document.getElementById("route-info");
  routeInfoContainer.innerHTML = ""; // 기존 내용 초기화

  features.forEach(function (feature, index) {
    if (index === currentWaypointIndex && feature.properties.description.includes("이동")) {
      alert("다음 안내 지점: " + feature.properties.description);
    }

    if (feature.properties.description.includes("이동")) {
      var info = document.createElement("div");
      info.classList.add("route-info-item");
      info.innerHTML = `<p>${feature.properties.description}</p>`;
      routeInfoContainer.appendChild(info);
    }
  });
  window.alert = ttsAlert;
}

async function checkRoute(currentLocation) {
  if (!currentMarker) {
    console.error("현재 위치 마커가 정의되지 않았습니다.");
    return;
  }

  // 폴리라인과의 최소 거리 계산
  var distanceToPolyline = getDistanceToPolyline(currentLocation, pathCoordinates);
  console.log("Polyline Distance: ", distanceToPolyline);

  // 경로 벗어남 체크
  if (distanceToPolyline > 50) {
    console.log("경로이탈");
    ttsAlert("경로를 벗어났습니다.");
    return;
  }

  if (currentWaypointIndex < waypoints.length) {
    var nextWaypoint = waypoints[currentWaypointIndex];
    var distanceToWaypoint = getDistance(currentLocation, nextWaypoint);

    if (distanceToWaypoint < 50) {
      currentWaypointIndex++;
    }
  } else {
    ttsAlert("경로를 완료했습니다.");
    await delay(5000); // 3초 대기
    localStorage.removeItem("routeData");
    window.location.reload();
    return;
  }

  // 목적지와의 거리 계산 및 도착 체크
  if (endMarker) {
    var distanceToDestination = getDistance(currentLocation, endMarker.getPosition());
    console.log(distanceToDestination);
    if (distanceToDestination < 10) {
      ttsAlert("도착 지점 근처에 도착했습니다. 경로 안내를 종료합니다.");
      await delay(6000); // 3초 대기
      localStorage.removeItem("routeData");
      window.location.reload();
      return;
    }
  } else {
    console.error("목적지 마커가 정의되지 않았습니다.");
  }
}
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
function getDistanceToPolyline(point, pathCoordinates) {
  var minDistance = Infinity;

  for (var i = 0; i < pathCoordinates.length - 1; i++) {
    var segmentStart = pathCoordinates[i];
    var segmentEnd = pathCoordinates[i + 1];
    var distance = getDistancePointToSegment(point, segmentStart, segmentEnd);
    if (distance < minDistance) {
      minDistance = distance;
    }
  }

  return minDistance;
}
function getDistancePointToSegment(point, segmentStart, segmentEnd) {
  var x0 = point.lng();
  var y0 = point.lat();
  var x1 = segmentStart.lng();
  var y1 = segmentStart.lat();
  var x2 = segmentEnd.lng();
  var y2 = segmentEnd.lat();

  var A = x0 - x1;
  var B = y0 - y1;
  var C = x2 - x1;
  var D = y2 - y1;

  var dot = A * C + B * D;
  var len_sq = C * C + D * D;
  var param = len_sq !== 0 ? dot / len_sq : -1;

  var xx, yy;

  if (param < 0) {
    xx = x1;
    yy = y1;
  } else if (param > 0 && param < 1) {
    xx = x1 + param * C;
    yy = y1 + param * D;
  } else {
    xx = x2;
    yy = y2;
  }

  var dx = x0 - xx;
  var dy = y0 - yy;

  return Math.sqrt(dx * dx + dy * dy) * 100000; // Distance in meters
}
function errorCallback(error) {
  console.error("Error getting GPS position: " + error.message);
}

function addMarker(type) {
  if (type === "start") {
    startLocation = new Tmapv2.LatLng(markerLatLng.lat(), markerLatLng.lng());
    startMarker = new Tmapv2.Marker({
      position: startLocation,
      map: map,
      title: "출발지",
    });
  } else {
    endLocation = new Tmapv2.LatLng(markerLatLng.lat(), markerLatLng.lng());
    endMarker = new Tmapv2.Marker({
      position: endLocation,
      map: map,
      title: "목적지",
    });
  }
  reverseGeo(markerLatLng.lat(), markerLatLng.lng(), function (address) {
    updateAddress(type, address);
  });
  infoWindow.setVisible(false);
}

function reverseGeo(lat, lng, callback) {
  var headers = {};
  headers["appKey"] = "po8JlsJs5W18L7GArJBDK5drZocbgJ116JTpWVN3";

  $.ajax({
    method: "GET",
    headers: headers,
    url: "https://apis.openapi.sk.com/tmap/geo/reversegeocoding?version=1&format=json&callback=result",
    async: false,
    data: {
      coordType: "WGS84GEO",
      addressType: "A10",
      lon: lng,
      lat: lat,
    },
    success: function (response) {
      var arrResult = response.addressInfo;
      var newRoadAddr = arrResult.city_do + " " + arrResult.gu_gun + " ";

      if (
        arrResult.eup_myun == "" &&
        (arrResult.legalDong.charAt(arrResult.legalDong.length - 1) == "읍" || arrResult.legalDong.charAt(arrResult.legalDong.length - 1) == "면")
      ) {
        newRoadAddr += arrResult.legalDong;
      } else {
        newRoadAddr += arrResult.eup_myun;
      }
      newRoadAddr += " " + arrResult.roadName + " " + arrResult.buildingIndex;

      if (
        arrResult.legalDong != "" &&
        arrResult.legalDong.charAt(arrResult.legalDong.length - 1) != "읍" &&
        arrResult.legalDong.charAt(arrResult.legalDong.length - 1) != "면"
      ) {
        if (arrResult.buildingName != "") {
          newRoadAddr += " (" + arrResult.legalDong + ", " + arrResult.buildingName + ") ";
        } else {
          newRoadAddr += " (" + arrResult.legalDong + ")";
        }
      } else if (arrResult.buildingName != "") {
        newRoadAddr += " (" + arrResult.buildingName + ") ";
      }

      var jibunAddr = arrResult.city_do + " " + arrResult.gu_gun + " " + arrResult.legalDong + " " + arrResult.ri + " " + arrResult.bunji;

      if (arrResult.buildingName != "") {
        jibunAddr += " " + arrResult.buildingName;
      }

      var address = "새주소 : " + newRoadAddr + "<br/>";
      address += "지번주소 : " + jibunAddr + "<br/>";
      address += "위경도좌표 : " + lat + ", " + lng;

      callback(address);
    },
    error: function (request, status, error) {
      console.log("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + error);
    },
  });
}

function updateAddress(type, address) {
  var addressDiv;

  if (type === "start") {
    addressDiv = document.getElementById("startAddress");
  } else if (type === "end") {
    addressDiv = document.getElementById("endAddress");
  }

  addressDiv.innerHTML = address;
}

// 아래는 poi 검색하는 부분이니까, 여기를 출발지, 목적지 구분해서 넣어줌
function searchLocation(searchKeyword, setFunction) {
  var headers = {};
  headers["appKey"] = "po8JlsJs5W18L7GArJBDK5drZocbgJ116JTpWVN3";

  $.ajax({
    method: "GET",
    headers: headers,
    url: "https://apis.openapi.sk.com/tmap/pois",
    data: {
      version: 1,
      format: "json",
      searchKeyword: searchKeyword,
      resCoordType: "EPSG3857",
      reqCoordType: "WGS84GEO",
      count: 10,
    },
    success: function (response) {
      var resultpoisData = response.searchPoiInfo.pois.poi;

      var innerHtml = "";
      var positionBounds = new Tmapv2.LatLngBounds();

      for (var k in resultpoisData) {
        var noorLat = Number(resultpoisData[k].noorLat);
        var noorLon = Number(resultpoisData[k].noorLon);
        var name = resultpoisData[k].name;
        var pointCng = new Tmapv2.Point(noorLon, noorLat);
        var projectionCng = new Tmapv2.Projection.convertEPSG3857ToWGS84GEO(pointCng);
        var lat = projectionCng._lat;
        var lon = projectionCng._lng;
        var markerPosition = new Tmapv2.LatLng(lat, lon);
        var marker = new Tmapv2.Marker({
          position: markerPosition,
          title: name,
          map: map,
        });

        innerHtml += "<li onclick='" + setFunction + "(" + lat + "," + lon + ")'><span>" + name + "</span></li>";

        markers.push(marker);
        positionBounds.extend(markerPosition);
      }

      $("#searchResult").html(innerHtml);
      map.panToBounds(positionBounds);
      map.zoomOut();
    },
    error: function (request, status, error) {
      console.error("Error:", error);
    },
  });
}

$("#startBtn").click(function () {
  var searchKeyword = $("#startKey").val();
  searchLocation(searchKeyword, "setStart");
});

$("#endBtn").click(function () {
  var searchKeyword = $("#endKey").val();
  searchLocation(searchKeyword, "setEnd");
});

function setStart(lat, lon) {
  $("#searchResult").html("");
  reverseGeo(lat, lon, function (address) {
    updateAddress("start", address);
  });
  clearMarkers();

  startLocation = new Tmapv2.LatLng(lat, lon);
  startMarker = new Tmapv2.Marker({
    position: startLocation,
    map: map,
    title: "출발지",
  });
  map.setCenter(startLocation);
  map.setZoom(13);
}
function setEnd(lat, lon) {
  $("#searchResult").html("");
  reverseGeo(lat, lon, function (address) {
    updateAddress("end", address);
  });
  clearMarkers();

  endLocation = new Tmapv2.LatLng(lat, lon);
  endMarker = new Tmapv2.Marker({
    position: endLocation,
    map: map,
    title: "목적지",
  });
  map.setCenter(endLocation);
  map.setZoom(13);
}

function clearMarkers() {
  if (markers.length > 0) {
    for (var i = 0; i < markers.length; i++) {
      markers[i].setMap(null);
    }
    markers = []; // 마커 배열 초기화
  }
}

function findRoute() {
  if (!startMarker && !endMarker) {
    console.error("출발지와 도착지를 모두 지정해주세요.");
    return;
  }

  // 경로 정보를 로컬 스토리지에 저장
  saveRouteToLocalStorage(startLocation, endLocation);

  sendLocations(startLocation, endLocation);
  // 5초마다 현재 위치 업데이트
  setInterval(function () {
    getCurrentLocation();
    console.log("현재 위치 업데이트");
  }, 5000);
  // 경로 체크
  setInterval(function () {
    console.log("check");
    console.log(currentMarker);
    checkRoute(currentMarker.getPosition());
  }, 10000); // 매 10초마다 경로 체크
}

function saveRouteToLocalStorage(startLocation, endLocation, currentWaypointIndex) {
  var routeData = {
    startLocation: [startLocation.lng(), startLocation.lat()],
    endLocation: [endLocation.lng(), endLocation.lat()],
    routeSearchStarted: true, // 경로 탐색 상태 표시
    currentWaypointIndex: currentWaypointIndex // 최근 도달한 인덱스 저장
  };

  localStorage.setItem('routeData', JSON.stringify(routeData));
}

function sendLocations(startLocation, endLocation) {
  routeSearchStarted = true; // 경로 탐색 시작

  if (infoWindow) {
    infoWindow.setVisible(false);
  }

  // 현위치, 출발지, 도착지 마커만 markers 배열에 남기기
  markers = [currentMarker, startMarker, endMarker];
  var csrftoken = getCookie("csrftoken");
  var data = {
    start_location: [startLocation.lng(), startLocation.lat()],
    end_location: [endLocation.lng(), endLocation.lat()],
  };
  console.log(JSON.stringify(data));
  fetch("/nav/location/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("네트워크 응답이 올바르지 않습니다");
      }
      return response.json();
    })
    .then((data) => {
      displayRoute(data);
    })
    .catch((error) => console.error("데이터를 가져오는 중 오류 발생:", error));
}

function updateCurrentLocationMarker(location) {
  if (!currentMarker) {
    currentMarker = new Tmapv2.Marker({
      position: location,
      map: map,
      title: "현재 위치",
    });
  } else {
    currentMarker.setPosition(location);
  }
  // 지도를 현재 위치로 이동
  map.panTo(location);
}

function updateRouteInfo(features) {
  var routeInfoContainer = document.getElementById("route-info");
  routeInfoContainer.innerHTML = "";

  var nextDescription = features[currentWaypointIndex].properties.description;
  console.log(nextDescription);
  var info = document.createElement("div");
  info.classList.add("route-info-item");
  info.innerHTML = `<p>다음 안내: ${nextDescription}</p>`;
  routeInfoContainer.appendChild(info);
}

// gpt한테 물어봄 해버시늄??처음들어봄
function getDistance(location1, location2) {
  // 두 위치 사이의 거리 계산 로직을 구현합니다.
  // 예를 들어, 두 지점의 위도 경도를 사용하여 실제 거리를 계산하는 방식을 적용할 수 있습니다.
  // 여기서는 간단히 거리를 반환하도록 하겠습니다.
  var lat1 = location1.lat();
  var lng1 = location1.lng();
  var lat2 = location2.lat();
  var lng2 = location2.lng();

  // 헤버시늄 공식(Haversine formula)을 사용하여 두 지점 사이의 거리를 계산합니다.
  var radLat1 = (Math.PI * lat1) / 180;
  var radLat2 = (Math.PI * lat2) / 180;
  var theta = lng1 - lng2;
  var radTheta = (Math.PI * theta) / 180;
  var dist = Math.sin(radLat1) * Math.sin(radLat2) + Math.cos(radLat1) * Math.cos(radLat2) * Math.cos(radTheta);
  dist = Math.acos(dist);
  dist = (dist * 180) / Math.PI;
  dist = dist * 60 * 1.1515;
  dist = dist * 1.609344 * 1000; // 단위를 미터로 변환

  return dist; // 거리를 미터 단위로 반환
}

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
function getCurrentLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(successCallback, errorCallback, {
      enableHighAccuracy: true,
      maximumAge: 0,
      timeout: 5000,
    });
  } else {
    alert("Geolocation is not supported by this browser.");
  }
}

function getCurrentLocation2() {
  return new Promise((resolve, reject) => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        position => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          const currentLatLng = new Tmapv2.LatLng(lat, lng);
          resolve(currentLatLng);
        },
        error => {
          reject(error);
        },
        {
          enableHighAccuracy: true,
          maximumAge: 0,
          timeout: 5000,
        }
      );
    } else {
      reject(new Error("Geolocation is not supported by this browser."));
    }
  });
}

function loadRouteFromLocalStorage() {
  var routeData = localStorage.getItem('routeData');
  if (routeData) {
    try {
      routeData = JSON.parse(routeData);

      // 기존 구조를 새 구조로 매핑
      var newRouteData = {
        start: {
          lat: routeData.intermediateWaypoint[1],
          lng: routeData.intermediateWaypoint[0]
        },
        destination: {
          lat: routeData.endLocation[1],
          lng: routeData.endLocation[0]
        },
        routeSearchStarted: routeData.routeSearchStarted
      };

      if (newRouteData.start.lat && newRouteData.start.lng &&
          newRouteData.destination.lat && newRouteData.destination.lng) {
        var startLatLng = new Tmapv2.LatLng(routeData.startLocation[1],routeData.startLocation[0]);
        var currentLatLng = new Tmapv2.LatLng(newRouteData.start.lat, newRouteData.start.lng);
        var endLatLng = new Tmapv2.LatLng(newRouteData.destination.lat, newRouteData.destination.lng);

        // 출발지와 도착지 마커 표시
        var startMarker = new Tmapv2.Marker({
          position: startLatLng,
          map: map,
          title: "출발지"
        });

        var endMarker = new Tmapv2.Marker({
          position: endLatLng,
          map: map,
          title: "도착지"
        });
        console.log("Start and end markers added to the map.");

        // 경로 안내 시작
        sendLocations(startLatLng, endLatLng);

        setInterval(function () {
          getCurrentLocation();
          console.log("현재 위치 업데이트");
          checkRoute(currentLatLng);
          console.log(currentLatLng);
        }, 5000);
      } else {
        console.error("Invalid route data structure:", newRouteData);
      }
    } catch (error) {
      console.error("Error parsing routeData JSON:", error);
    }
  } else {
    console.log("No route data found in localStorage. Route guidance not started.");
  }
}

document.addEventListener("DOMContentLoaded", function () {
  initMap(); 
  var routeData = localStorage.getItem('routeData');
  if (routeData) {
    loadRouteFromLocalStorage();
  } else {
    console.log("로컬 스토리지에서 경로 데이터를 찾을 수 없습니다. 경로 안내를 시작하지 않았습니다.");
  }
});