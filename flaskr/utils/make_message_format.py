from flask_login import current_user
from flask import url_for

def make_message_format(user, messages):
    not_image = "user_icon/not_icon.svg"
    message_tag = ''
    for message in messages:
        message_tag += '<div class="col-lg-1 offset-lg-3">'
        if user.icon_dir:
            message_tag += f'<img class="icon_img_circle_mini" src={url_for("static", filename=user.icon_dir)} alt="">'
        else :
            message_tag += f'<img class="icon_img_circle_mini" src="{url_for("static", filename=not_image)} alt="">'
        message_tag += f'''
            { user.name }
            </div>
            <div class="speech-bubble-dest user-info-mini col-lg-3">
            <p>{message.message}</p>
            </div>
            <div class="col-lg-1"></div>
        ''' 

    return message_tag