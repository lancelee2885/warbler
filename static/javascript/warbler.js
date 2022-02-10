"use strict";
const GET_URL = window.location;
const BASE_URL = GET_URL.protocol + "//" + GET_URL.host + "/" + GET_URL.pathname.split('/')[0];

async function likeClickHandler(evt){
    evt.preventDefault();
    let messageId = $(evt.target).attr("id");
    let csrfToken = $(evt.target).find("input").val()
    // console.log($(evt.target))
    const response = await axios({
      url: `${BASE_URL}/messages/${messageId}/like`,
      method: "POST",
      data: {
        "csrf_token": csrfToken
      }
    });

    $(evt.target).find("i").toggleClass("fas far");
    

    return false;
}


$(".container").on("submit", ".like-btn-form", likeClickHandler);
