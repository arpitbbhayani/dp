function showError(error) {
    alert(error);
}

function showMessage(message) {
    alert(message);
}

function validateChangePassword(form) {

    return true;
}

function registerUser(form) {
    var email = form.elements["email"].value.trim();
    var username = form.elements["username"].value.trim();
    var pass = form.elements["password"].value.trim();
    var confirmpass = form.elements["cpassword"].value.trim();

    if (!(pass && confirmpass && email && username)) {
        return showError("Email, Username, Password are mandatory");
    }

    if (pass !== confirmpass) {
        return showError("Password and Confirm Password does not match");
    }

    $.post('/register', {
        email: email,
        username: username,
        pass: pass,
    }).done(function(response) {
        showMessage(response.message);
    }).fail(function(xhr, status, error) {
        return showError(error);
    });
}

function changePassword(form) {
    var pass = form.elements["pass"].value;
    var confirmpass = form.elements["confirmpass"].value;
    if (pass !== confirmpass) {
        showError("Password & Confirm Password does not match");
    }

    $.post('/settings/password/change', {
        pass: form.elements["pass"].value,
        confirmpass: form.elements["confirmpass"].value
    }).done(function(response) {
        if(response.error) {
            return showError(response.message);
        }
        showMessage(response.message);
    }).fail(function(xhr, status, error) {
        return showError(error);
    });
}

function updateUsername(form) {

    if (!form.elements["username"]) {
        return;
    }

    $.post('/settings/username/change', {
        username: form.elements["username"].value,
    }).done(function(response) {
        if(response.error) {
            return showError(response.message);
        }
        showMessage(response.message);
    }).fail(function(xhr, status, error) {
        return showError(error);
    });
}

function searchUsers(form) {
    query = form.elements["q"].value;
    $.get('/admin/search/users?out=html&q=' + query, {
    }).done(function(response) {
        $('#user-search-results').html(response);
    }).fail(function(xhr, status, error) {
        showError(error);
    });
}

function createUser(form) {
    $.post('/admin/users', {
        email: form.elements["email"].value,
        pass: form.elements["password"].value,
        username: form.elements["username"].value,
    }).done(function(response) {
        if(response.error) {
            return showError(response.message);
        }
        showMessage(response.message);
    }).fail(function(xhr, status, error) {
        return showError(error);
    });
}

function updateUser(form) {
    $.post('/admin/users/' + form.elements["id"].value, {
        pass: form.elements["password"].value,
    }).done(function(response) {
        if(response.error) {
            return showError(response.message);
        }
        showMessage(response.message);
    }).fail(function(xhr, status, error) {
        return showError(error);
    });
}

function createTask(form) {
    if (!form.elements["task"].value) {
        return showError("Task cannot be empty");
    }
    $.post('/tasks', {
        task: form.elements["task"].value,
    }).done(function(response) {
        if(response.error) {
            return showError(response.message);
        }
        showMessage(response.message);
        location.reload(true);
    }).fail(function(xhr, status, error) {
        return showError(error);
    });
}

function markTask(checkbox) {
    $.post('/tasks/' + checkbox.getAttribute('value'), {
        isCompleted: checkbox.checked
    }).done(function(response) {
        if(response.error) {
            return showError(response.message);
        }
        showMessage(response.message);
        location.reload(true);
    }).fail(function(xhr, status, error) {
        return showError(error);
    });
}

function updateTask(form) {
    var taskid = form.elements['taskid'].value;
    var task = form.elements['task'].value;
    $.post('/tasks/' + taskid, {
        task: task
    }).done(function(response) {
        if(response.error) {
            return showError(response.message);
        }
        showMessage(response.message);
        window.location = '/tasks/' + taskid;
    }).fail(function(xhr, status, error) {
        return showError(error);
    });
}

function commentTask(form) {
    var taskid = form.elements["taskid"].value;
    var comment = form.elements["comment"].value;
    $.post('/tasks/' + taskid + "/comments", {
        comment: comment
    }).done(function(response) {
        if(response.error) {
            return showError(response.message);
        }
        showMessage(response.message);
        location.reload(true);
    }).fail(function(xhr, status, error) {
        return showError(error);
    });
}

function loadComments(taskid, selector) {
    $(selector).addClass('loading');
    $.get('/tasks/' + taskid + '/comments?out=html', {
    }).done(function(response) {
        $(selector).html(response);
    }).fail(function(xhr, status, error) {
        showError(error);
    }).always(function() {
        $(selector).removeClass('loading');
    });
}

$(document).ready(function() {
    $(".ui.dropdown").dropdown();
})
