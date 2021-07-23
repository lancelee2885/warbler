"use strict";
const BASE_URL = "http://localhost:5000";

async function likeClickHandler(evt){
    evt.preventDefault();
    let messageId = $(evt.target).attr("id");
    let csrfToken = $("#csrf_token")
    
    const response = await axios({
      url: `${BASE_URL}/messages/${messageId}/like`,
      method: "POST",
      params: 
    });
    
    console.log(response);

    return false
}


$(".container").on("submit", ".like-btn-form", likeClickHandler);