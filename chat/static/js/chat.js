function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function message_received(data){
    const main_chat_div = document.getElementById("main_chat");
    let main_chat_type = main_chat_div.getAttribute("data-chat_type");
    let main_chat_pk = main_chat_div.getAttribute("data-chat_pk");
    const messages_div = document.getElementById("chat_messages");

    if (main_chat_type == data.chat_type && main_chat_pk == data.chat_pk && messages_div != null){
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
    last_message.innerHTML = data.author_name + ": " + data.message;

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


function set_dropwdowns_in_manage_chat(){
    document.querySelectorAll(".manage_user_dropdown_button").forEach(element => element.addEventListener('click', function(){
        console.log(element.parentNode.querySelector(".dropdown-content"));
        console.log(element.parentNode.querySelector(".dropdown-content").classList);
        element.parentNode.querySelector(".dropdown-content").classList.toggle("show");
    }));

    // Close the dropdown menu if the user clicks outside of it
    window.onclick = function(event) {
        if (!event.target.matches('.manage_user_dropdown_button')) {
            var dropdowns = document.getElementsByClassName("dropdown-content");
            var i;
            for (i = 0; i < dropdowns.length; i++) {
                var openDropdown = dropdowns[i];
                if (openDropdown.classList.contains('show')) {
                    openDropdown.classList.remove('show');
                }
            }
        }
    }
}

function set_remove_user_from_chat(event){
    const element = event.target;
    const user_pk = element.parentElement.parentElement.getAttribute("data-user_pk");
    const chat_pk = document.getElementById("main_chat").getAttribute("data-chat_pk");
    const csrf_token = getCookie('csrftoken');
    const url = "group-chat-remove-user/";
    var options = {
        method: 'POST',
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin'
    }
    var post_data = new FormData();
    post_data.append('chat_pk', chat_pk);
    post_data.append('user_pk', user_pk);
    options['body'] = post_data;

    fetch(url, options)
    .then(response => response.json())
    .then(data => {
        if (data['status'] != "error"){
            element.parentElement.parentElement.parentElement.remove();
        }
    });
}


function set_add_user_to_admins(event){
    const element = event.target;
    const parent = element.parentElement;
    const user_pk = parent.parentElement.getAttribute("data-user_pk");
    const chat_pk = document.getElementById("main_chat").getAttribute("data-chat_pk");
    const csrf_token = getCookie('csrftoken');
    const url = "group-chat-add-to-admins/";
    var options = {
        method: 'POST',
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin'
    }
    var post_data = new FormData();
    post_data.append('chat_pk', chat_pk);
    post_data.append('user_pk', user_pk);
    options['body'] = post_data;

    fetch(url, options).
    then(response => response.json()).
    then(data => {
        if (data['status'] != "error"){
            element.remove();
            var remove_from_admins_div = document.createElement("div");
            remove_from_admins_div.innerHTML = "Remove from admins";
            remove_from_admins_div.classList.add("remove_from_admins");
            remove_from_admins_div.addEventListener('click', set_remove_user_from_admins);
            parent.appendChild(remove_from_admins_div);
            parent.parentElement.parentElement.parentElement.classList.remove("participant_div");
            parent.parentElement.parentElement.parentElement.classList.add("chat_admin_div");
            if (document.getElementById("chat_admins_wrapper").innerText === "There are no admins"){
                document.getElementById("chat_admins_wrapper").innerText = "";
            }
            document.getElementById("chat_admins_wrapper").appendChild(parent.parentElement.parentElement.parentElement);
            if (document.getElementById("rest_participants_list").innerHTML.trim() === ""){
                document.getElementById("rest_participants_list").innerText = "There aren't any other participants";
            }
        }
    });
}


function set_remove_user_from_admins(event){
    const element = event.target;
    const parent = element.parentElement;
    const user_pk = parent.parentElement.getAttribute("data-user_pk");
    const chat_pk = document.getElementById("main_chat").getAttribute("data-chat_pk");
    const csrf_token = getCookie('csrftoken');
    const url = "group-chat-remove-from-admins/";
    var options = {
        method: 'POST',
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin'
    }
    var post_data = new FormData();
    post_data.append('chat_pk', chat_pk);
    post_data.append('user_pk', user_pk);
    options['body'] = post_data;

    fetch(url, options).
    then(response => response.json()).
    then(data => {
        if (data['status'] != "error"){
            element.remove();
            var add_to_admins_div = document.createElement("div");
            add_to_admins_div.innerHTML = "Add to admins";
            add_to_admins_div.classList.add("add_to_admins");
            add_to_admins_div.addEventListener('click', set_add_user_to_admins);
            parent.appendChild(add_to_admins_div);
            parent.parentElement.parentElement.parentElement.classList.remove("chat_admin_div");
            parent.parentElement.parentElement.parentElement.classList.add("participant_div");
            if (document.getElementById("rest_participants_list").innerText === "There aren't any other participants"){
                document.getElementById("rest_participants_list").innerText = "";
            }
            document.getElementById("rest_participants_list").appendChild(parent.parentElement.parentElement.parentElement);
            if (document.getElementById("chat_admins_wrapper").innerHTML.trim() === ""){
                document.getElementById("chat_admins_wrapper").innerText = "There are no admins";
            }
        }
    });
}

function set_transfer_ownership(event){
    if (window.confirm("Do you really want to transfer ownership of this chat? This action is irreversible.")){
        const element = event.target;
        const parent = element.parentElement;
        const user_pk = parent.parentElement.getAttribute("data-user_pk");
        const chat_pk = document.getElementById("main_chat").getAttribute("data-chat_pk");
        const csrf_token = getCookie('csrftoken');
        const url = "group-chat-transfer-ownership/";
        var options = {
            method: 'POST',
            headers: {'X-CSRFToken': csrf_token},
            mode: 'same-origin'
        }
        var post_data = new FormData();
        post_data.append('chat_pk', chat_pk);
        post_data.append('user_pk', user_pk);
        options['body'] = post_data;

        fetch(url, options).
        then(response => response.json()).
        then(data => {
            if (data['status'] === "ok"){
                change_view_to_manage_chat(document.getElementById("main_chat"));
                document.getElementById("leave_chat").removeAttribute("title");
                document.getElementById("leave_chat_button").removeAttribute("disabled")
            }
        });
    }
}


function set_delete_chat(event){
    if (window.confirm("Do you really want to delete this chat? This action is irreversible.")){
        const chat_pk = document.getElementById("main_chat").getAttribute("data-chat_pk");
        const csrf_token = getCookie('csrftoken');
        const url = "group-chat-delete/";
        var options = {
            method: 'POST',
            headers: {'X-CSRFToken': csrf_token},
            mode: 'same-origin'
        }
        var post_data = new FormData();
        post_data.append('chat_pk', chat_pk);
        options['body'] = post_data;

        fetch(url, options).
        then(response => response.json()).
        then(data => {
            if (data['status'] === "ok"){
                document.querySelector(`.chat_element[data-chat_pk="${chat_pk}"][data-chat_type="group_chat"]`).remove()
                document.getElementById("main_chat").innerHTML = "";
            }
        });
    }
}


function set_links_in_manage_chat(){
    document.querySelectorAll(".remove_from_group").forEach(element => element.addEventListener('click', set_remove_user_from_chat));
    document.querySelectorAll(".add_to_admins").forEach(element => element.addEventListener('click', set_add_user_to_admins));
    document.querySelectorAll(".remove_from_admins").forEach(element => element.addEventListener('click', set_remove_user_from_admins));
    document.querySelectorAll(".transfer_ownership").forEach(element => element.addEventListener('click', set_transfer_ownership));
    document.getElementById("remove_group_button").addEventListener('click', set_delete_chat);
}


function set_manage_chat_name_form(){
    let name_form = document.getElementById("name_form");
    name_form.addEventListener('submit', function(event){
        event.preventDefault();
        const chat_name = name_form.querySelector("#id_group_name_input").value;
        const chat_pk = document.getElementById("main_chat").getAttribute("data-chat_pk");
        const csrf_token = getCookie('csrftoken');
        const url = "group-chat-change-name/";
        var options = {
            method: 'POST',
            headers: {'X-CSRFToken': csrf_token},
            mode: 'same-origin'
        }
        var post_data = new FormData();
        post_data.append('chat_pk', chat_pk);
        post_data.append('new_name', chat_name);
        options['body'] = post_data;
        fetch(url, options).
        then(response => response.json()).
        then(data => {
            if (data['status'] === "ok"){
                document.getElementById("chat_name").innerText = chat_name;
                document.querySelector(`.chat_element[data-chat_pk="${chat_pk}"][data-chat_type="group_chat"]`).querySelector(".chat_element_name").innerText = chat_name;
            }
        });

    });
}


function set_manage_chat_image_form(){
    let image_form = document.getElementById("image_form");
    image_form.addEventListener('submit', function(event){
        event.preventDefault();
        const chat_name = name_form.querySelector("#id_group_name_input").value;
        const chat_pk = document.getElementById("main_chat").getAttribute("data-chat_pk");
        const csrf_token = getCookie('csrftoken');
        const url = "group-chat-change-image/";
        var options = {
            method: 'POST',
            headers: {'X-CSRFToken': csrf_token},
            mode: 'same-origin'
        }
        var post_data = new FormData();
        post_data.append('chat_pk', chat_pk);
        let image_input = document.getElementById("id_group_image_input");
        post_data.append('image', image_input.files[0]);
        options['body'] = post_data;
        fetch(url, options).
        then(response => response.json()).
        then(data => {
            if (data['status'] === "ok"){
                document.getElementById("chat_image_manage_chat").src = data['image_url'];
                document.querySelector(`.chat_element[data-chat_pk="${chat_pk}"][data-chat_type="group_chat"]`).querySelector(".chat_element_image").src = data['image_url'];
                document.getElementById("chat_header_image").src = data['image_url'];

                let new_image_input = document.createElement("input");
                new_image_input.type = image_input.type;
                new_image_input.id = image_input.id;
                new_image_input.name = image_input.name;
                new_image_input.accept = image_input.accept;
                image_input.parentNode.replaceChild(new_image_input, image_input);
            }
        });

    });
}


function set_add_user_to_chat_divs(){
    const csrf_token = getCookie('csrftoken');
    const add_user_url = "group-chat-add-user/";
    const chat_pk = document.getElementById("main_chat").getAttribute("data-chat_pk");
    document.querySelectorAll(".add_user_div").forEach(element => element.addEventListener('click', function(){
        var options = {
            method: 'POST',
            headers: {'X-CSRFToken': csrf_token},
            mode: 'same-origin'
        }
        let user_pk = element.getAttribute("data-user_pk");
        var post_data = new FormData();
        post_data.append('chat_pk', chat_pk);
        post_data.append('user_pk', user_pk);
        options['body'] = post_data;

        fetch(add_user_url, options)
        .then(response => response.json())
        .then(data => {
            if (data['status'] != "error"){
                element.parentElement.remove();
            }
        });

    }));
}


function set_users_search_add_user(){
    const search_input = document.getElementById("search_user");
    let addable_users = document.querySelectorAll(".chat_user");
    if (search_input != null){
        search_input.addEventListener("keyup", function(){
            if (search_input.value.replace(/\s+/g, '') == ""){
                for (var i = 0, len = addable_users.length; i < len; i++) {
                    addable_users[i].style.display = "flex";
                }
                return;
            }

            for (var i = 0, len = addable_users.length; i < len; i++) {
                addable_users[i].style.display = "none";
            }

            var search_strings = search_input.value.toUpperCase().split(/\W/);
            for (var i = 0, len = search_strings.length; i < len; i++) {
                var current_search = search_strings[i].toUpperCase();
                if (current_search !== "") {
                    for (var j = 0, divs_len = addable_users.length; j < divs_len; j++) {
                        if (addable_users[j].querySelector("a").textContent.toUpperCase().indexOf(current_search) !== -1) {
                            addable_users[j].style.display = "flex";
                        }
                    }
                }

            }
        });
    }
}



function set_chat_links(main_chat_div){
    const options = {
        method: 'GET',
        mode: 'same-origin'
    }
    const chat_pk = main_chat_div.getAttribute("data-chat_pk");

    if (main_chat_div.querySelector("#chat_info_button") != null){
        main_chat_div.querySelector("#chat_info_button").addEventListener('click', function(){
            console.log("chat info button clicked");
            const url_chat_info = "/chat/group-chat-info/" + chat_pk + "/";
            fetch(url_chat_info, options).then(response => response.json()).then(data => {
                if (data["status"] === "ok"){
                    main_chat_div.querySelector("#chosen_chat_content_wrapper").innerHTML = data['rendered_template'];
                    main_chat_div.querySelector("#return_to_messages_button").addEventListener('click', function(){
                        set_chosen_chat(main_chat_div, "group_chat", chat_pk);
                    });
                }
            });
        });
    }

    if (main_chat_div.querySelector("#add_users_button") != null){
        main_chat_div.querySelector("#add_users_button").addEventListener('click', function(){
            console.log("add users button clicked");
            const url_add_users = "/chat/group-chat-add-users/" + chat_pk + "/";
            fetch(url_add_users, options).then(response => response.json()).then(data => {
                if (data['status'] != "error"){
                    main_chat_div.querySelector("#chosen_chat_content_wrapper").innerHTML = data['rendered_template'];
                    main_chat_div.querySelector("#return_to_messages_button").addEventListener('click', function(){
                        set_chosen_chat(main_chat_div, "group_chat", chat_pk);
                    });
                    set_add_user_to_chat_divs();
                    set_users_search_add_user();
                }
            });
        });
    }

    if (main_chat_div.querySelector("#manage_chat") != null){
        main_chat_div.querySelector("#manage_chat_button").addEventListener('click', function(){
            change_view_to_manage_chat(main_chat_div);
        });
    }

    if (main_chat_div.querySelector("#leave_chat") != null){
        document.getElementById("leave_chat_button").addEventListener('click', function(){
            if (window.confirm("Do you really want to leave this chat?")){
                const chat_pk = main_chat_div.getAttribute("data-chat_pk");
                const csrf_token = getCookie('csrftoken');
                const url = "group-chat-leave/";
                var options = {
                    method: 'POST',
                    headers: {'X-CSRFToken': csrf_token},
                    mode: 'same-origin'
                }
                var post_data = new FormData();
                post_data.append('chat_pk', chat_pk);
                options['body'] = post_data;
                fetch(url, options).
                then(response => response.json()).
                then(data => {
                    if (data['status'] === "ok"){
                        document.querySelector(`.chat_element[data-chat_pk="${chat_pk}"][data-chat_type="group_chat"]`).remove()
                        document.getElementById("main_chat").innerHTML = "";
                    }
                });
            }
        });
    }
}


function change_view_to_manage_chat(main_chat_div){
    const options = {
        method: 'GET',
        mode: 'same-origin'
    }
    const chat_pk = main_chat_div.getAttribute("data-chat_pk");
    const url_manage_chat = "/chat/group-chat-manage/" + chat_pk + "/";
    fetch(url_manage_chat, options).then(response => response.json()).then(data => {
        if (data['status'] != "error"){
            main_chat_div.querySelector("#chosen_chat_content_wrapper").innerHTML = data['rendered_template'];
            set_dropwdowns_in_manage_chat();
            set_links_in_manage_chat();
            set_manage_chat_name_form();
            set_manage_chat_image_form();
            main_chat_div.querySelector("#return_to_messages_button").addEventListener('click', function(){
                set_chosen_chat(main_chat_div, "group_chat", chat_pk);
            });
        }
    });
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


function set_infinite_scroll_pagination_in_chat(){
    let chat_messages_div = document.getElementById("chat_messages");
    chat_messages_div.addEventListener('scroll', function(){
        if (chat_messages_div.scrollTop == 0){
            let chosen_chat_content_wrapper = document.getElementById("chosen_chat_content_wrapper");
            let is_more_messages = (chosen_chat_content_wrapper.getAttribute("data-has_previous_page").toLowerCase() === "true");
            if (is_more_messages){
                let first_cursor = chosen_chat_content_wrapper.getAttribute("data-first_cursor");
                let chat_pk = document.getElementById("main_chat").getAttribute("data-chat_pk");
                let chat_type = document.getElementById("main_chat").getAttribute("data-chat_type");
                let url = (chat_type == "group_chat") ? "/chat/group-chat/paginated-messages/" : "/chat/private-chat/paginated-messages/";
                url += chat_pk + "/" + first_cursor + "/";
                let options = {
                    method: 'GET',
                    mode: 'same-origin'
                }
                fetch(url, options).then(response => response.json()).then(data => {
                    if (data['status'] === "ok"){
                        let old_scroll_height = chat_messages_div.scrollHeight;
                        chat_messages_div.insertAdjacentHTML("afterbegin", data["rendered_template"]);
                        chat_messages_div.scrollTop = chat_messages_div.scrollHeight - old_scroll_height;
                        chosen_chat_content_wrapper.setAttribute("data-first_cursor", data["first_cursor"]);
                        chosen_chat_content_wrapper.setAttribute("data-has_previous_page", data["has_previous_page"]);
                    }
                });
            }
        }
    });
}


function set_chosen_chat(main_chat_div, chat_type, chat_pk){
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
            document.getElementById("message_input").addEventListener("keypress", function(event){
                if (event.key === "Enter" && !event.shiftKey){
                    event.preventDefault();
                    document.getElementById("message_form").dispatchEvent(new Event('submit', {cancelable: true}));
                }
            });
            var chat_messages_div = document.getElementById("chat_messages");
            chat_messages_div.scrollTop = chat_messages_div.scrollHeight;

            if (chat_type == "group_chat"){
                set_chat_links(main_chat_div);
            }
            set_infinite_scroll_pagination_in_chat();
        }
    });
}


function set_create_group_chat_button(){
    const create_group_chat_button = document.getElementById("create_chat_button");
    create_group_chat_button.addEventListener('click', function(){
        const csrf_token = getCookie('csrftoken');
        const url = "group-chat-create/";
        var options = {
            method: 'GET',
            mode: 'same-origin'
        }
        fetch(url, options).then(response => response.json()).then(data => {
            if (data['status'] === "ok"){
                const main_chat_div = document.getElementById("main_chat");
                main_chat_div.innerHTML = data['rendered_template'];
                set_create_chat_form();
                unselect_all_chat_elements();
            }
        });
    });
}

function set_create_chat_form(){
    const create_chat_form = document.getElementById("create_chat_form");
    create_chat_form.addEventListener('submit', function(event){
        event.preventDefault();
        const csrf_token = getCookie('csrftoken');
        const url = "group-chat-create/";
        var options = {
            method: 'POST',
            // headers: {'X-CSRFToken': csrf_token},
            mode: 'same-origin'
        }
        var post_data = new FormData(create_chat_form);
        options['body'] = post_data;
        fetch(url, options).
        then(response => response.json()).
        then(data => {
            if (data['status'] === "ok"){
                let chats_list = document.getElementById("chats_list");
                chats_list.insertAdjacentHTML('beforeend', data['rendered_template']);
                let new_chat_element = chats_list.querySelector(`.chat_element[data-chat_pk="${data['chat_pk']}"][data-chat_type="group_chat"]`);
                new_chat_element.addEventListener('click', function(){
                    set_chosen_chat(document.getElementById("main_chat"), "group_chat", data['chat_pk']);
                });
                set_chosen_chat(document.getElementById("main_chat"), "group_chat", data['chat_pk']);
            }
        });
    });
}

function unselect_all_chat_elements(){
    document.querySelectorAll('.chat_element').forEach(element => element.classList.remove("selected_chat_element"));
}


window.addEventListener('DOMContentLoaded', function () {
    const main_chat_div = document.getElementById("main_chat");

    document.querySelectorAll('.chat_element').forEach(element => element.addEventListener('click', function(){
        let chat_type = element.getAttribute("data-chat_type");
        let chat_pk = element.getAttribute("data-chat_pk");
        set_chosen_chat(main_chat_div, chat_type, chat_pk);
        unselect_all_chat_elements();
        element.classList.add("selected_chat_element");
    }));
    set_create_group_chat_button();

    connect();

});

