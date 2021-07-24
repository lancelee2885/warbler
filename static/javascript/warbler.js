"use strict";
const BASE_URL = "http://localhost:5000";

async function likeClickHandler(evt){
    evt.preventDefault();
    let messageId = $(evt.target).attr("id");
    let csrfToken = $(evt.target).parent.val()
    
    const response = await axios({
      url: `${BASE_URL}/messages/${messageId}/like`,
      method: "POST",
      data: {
        "csrf_token": csrfToken
      }
    });


    
    console.log(response);

    return false
}


$(".container").on("submit", ".like-btn-form", likeClickHandler);

//csrf_token: IjliYzM0ODljNTBhZjc3YzczYzlkYWZiNjNkZDg0NGJkYTU2ZjJmYjgi.YPtWvQ.UX0VgYVAT022lymMuGzCbU79zZg