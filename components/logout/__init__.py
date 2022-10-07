# from flask_login import LoginManager
from flask_login import logout_user, login_required
from flask import Blueprint
from flask import redirect, session

# login_manager = LoginManager()


logout_blueprint = Blueprint('logout', __name__, template_folder='templates', static_folder='static')


@logout_blueprint.route('/')
@login_required
def render_logout():
    cart=session.get('cart')
    user_id=session.get('_user_id')
    carts_users=session.get('carts_users', [])
    cart_user={}
    if len(carts_users) == 0:
        cart_user['user_id']=user_id
        cart_user['cart'] = cart

    else:
        for cart_user in carts_users:
            if cart_user['user_id'] == user_id:
                cart_user['cart'] = cart
            else:
                cart_user['user_id'] = user_id
                cart_user['cart'] = cart

    carts_users.append(cart_user)
    session['carts_users'] = carts_users
    session['cart']=[]

    logout_user()

    print('session=', session)
    # session.pop('user_id')
    # session.pop('user_email')
    return redirect('/')

