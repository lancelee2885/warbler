"use strict";
const BASE_URL = "http://localhost:5000";

async function likeClickHandler(evt){
    evt.preventDefault();
    let messageId = $(evt.target).attr("id");
    
    const response = await axios({
      url: `${BASE_URL}/messages/${messageId}/like`,
      method: "POST",
    });
    
    console.log(response);
    
}


$(".container").on("submit", "i", likeClickHandler);