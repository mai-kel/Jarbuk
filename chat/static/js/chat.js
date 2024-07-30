function message_received(data){
    const main_chat_div = document.getElementById("main_chat");
    let main_chat_type = main_chat_div.getAttribute("data-chat_type");
    let main_chat_pk = main_chat_div.getAttribute("data-chat_pk");

    if (main_chat_type == data.chat_type && main_chat_pk == data.chat_pk){
        const messages_div = document.getElementById("chat_messages");
        const url =  (data.message_type == "group_message") ? "/chat/group-message/" + data.message_pk + "/" : "/chat/private-message/" + data.message_pk + "/";
        var options = {
            method: 'GET',
            mode: 'same-origin'
        }

        // send HTTP request
        fetch(url, options)
        .then(response => response.json())
        .then(data => {
            if (data['status'] != "error"){
                var chat_messages_div = document.getElementById("chat_messages");
                var scroll_value = chat_messages_div.scrollHeight - chat_messages_div.clientHeight - chat_messages_div.scrollTop;
                messages_div.innerHTML += data['rendered_message'];
                if (scroll_value < 200){
                    chat_messages_div.scrollTop = chat_messages_div.scrollHeight;
                }
            }
        });
    }

    // update last message in chat list
    const chat_element = document.querySelector(`.chat_element[data-chat_type="${data.chat_type}"][data-chat_pk="${data.chat_pk}"]`);
    const last_message = chat_element.querySelector(".chat_last_message");
    last_message.innerHTML = data.message;

    // move chat to top
    var top_chat_element = document.querySelector('.chat_element');
    top_chat_element.parentNode.insertBefore(chat_element, top_chat_element);

}

function connect() {
    chatSocket = new WebSocket("ws://" + window.location.host + "/ws/chat/");

    chatSocket.onopen = function(e) {
        console.log("Successfully connected to the WebSocket.");
    }

    chatSocket.onclose = function(e) {
        console.log("WebSocket connection closed unexpectedly. Trying to reconnect in 2s...");
        setTimeout(function() {
            console.log("Reconnecting...");
            connect();
        }, 2000);
    };

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log(data);

        switch (data.type) {
            default:
                message_received(data);
                break;
        }
    }

}

function chat_form_submit(event){
    event.preventDefault();
        const message_input = document.getElementById("message_input");
        const message = message_input.value;
        var chat_pk = document.getElementById("main_chat").getAttribute("data-chat_pk");
        var chat_type = document.getElementById("main_chat").getAttribute("data-chat_type");

        const data = {
            "message": message,
            "chat_pk": chat_pk,
            "chat_type": chat_type
        }

        chatSocket.send(JSON.stringify(data));
        message_input.value = "";
    }


window.addEventListener('DOMContentLoaded', function () {
    const main_chat_div = document.getElementById("main_chat");

    document.querySelectorAll('.chat_element').forEach(element => element.addEventListener('click', function(){
        let chat_type = element.getAttribute("data-chat_type");
        let chat_pk = element.getAttribute("data-chat_pk");

        const url = (chat_type == "group_chat") ? "/chat/group-chat/" + chat_pk + "/" : "/chat/private-chat/" + chat_pk + "/";
        let options = {
            method: 'GET',
            mode: 'same-origin'
        }

        fetch(url, options).then(response => response.json()).then(data => {
            if (data['status'] != "error"){
                main_chat_div.innerHTML = data['rendered_chat'];
                main_chat_div.setAttribute("data-chat_type", chat_type);
                main_chat_div.setAttribute("data-chat_pk", chat_pk);
                document.getElementById("message_form").addEventListener('submit', chat_form_submit);
                var chat_messages_div = document.getElementById("chat_messages");
                chat_messages_div.scrollTop = chat_messages_div.scrollHeight;
            }
        });
    }));

    connect();

});

