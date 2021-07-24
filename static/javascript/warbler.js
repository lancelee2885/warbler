"use strict";
const BASE_URL = "http://localhost:5000";

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
