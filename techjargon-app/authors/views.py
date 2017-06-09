from django.shortcuts import render
from django.shortcuts import redirect
from auth0.v3.authentication import GetToken
from auth0.v3.authentication import Users
from django.contrib.auth.models import User
from authors.models.author import Author
import pdb;
import json
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


# Create your views here.

def signin(request):
    from django.contrib.auth import authenticate, login, logout
    logout(request)

    _user = None
    _login_success = False
    _message = None

    if request.POST:
        from django.contrib.auth import authenticate
        # pdb.set_trace()
        _username = request.POST['username']
        _password = request.POST['password']
        _user = authenticate(username=_username, password=_password)
        # pdb.set_trace()
        if _user is not None:
            if _user.is_active:
                login(request=request, user=_user)
                _login_success = True
                _message = "Login Success"
            else:
                _message = "User has been deactivated"
        else:
            _message = "Invalid credentials"

    if _login_success:
        if _user.is_staff:
            return redirect('/')
        else:
            return redirect('/')
    else:
        return render(request, 'authors/signin.html', {'error': _message})


def signout(request):
    from django.contrib.auth import authenticate, login, logout
    logout(request)
    del request.session['profile']
    return redirect('/')

def auth0_callback(request):
    code = request.GET.get('code')
    get_token = GetToken('techjargon.auth0.com')
    auth0_users = Users('techjargon.auth0.com')
    token = get_token.authorization_code('QADeAHqjls_NxG6lnY_MQiqJ2wErFUpx',
                                         '00I5NqJtwLDZBBUBXQLTYLL195BvPMDZ3uFqc6OcnunuOsyuYvI7cCQ0tORWre4a', code, 'http://techjargon-dev.fidenz.info/authors/callback/')
    user_info = auth0_users.userinfo(token['access_token'])
    user = json.loads(user_info)
    request.session['profile'] = user
    flag, message = __check_n_register(user)
    if flag:
        _user = User.objects.get(email=user['email'])
        _user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, _user)
        return redirect('/')
    else:
        return redirect('/authors/signin/')


# private

def __check_n_register(userj):
    flag = False
    message = []
    try:
        _user, _created = User.objects.get_or_create(username=__build_username(userj['name']), email=userj['email'], first_name=userj["given_name"], last_name=userj["family_name"])
        try:
            if _user.author:
                # _user.author.profil_pic.path = userj['picture']
                _user.author.save()

        except Author.DoesNotExist as e:
            _author = Author(role=Author._DEFAULT_TYPE)
            # _author.profil_pic.path = userj['picture']
            _author.user = _user
            _author.save()
            message.append("Author created successfully")
            pass

        except IntegrityError as e:
            message.append(e)
            pass

    except IntegrityError as e:
        message.append(e)
        pass
    else:
        message.append("User created successfully")
        flag = True

    return flag, message


def __build_username(fullname):
    _name_frags = fullname.split()
    username = _name_frags[0]
    if len(_name_frags) > 1:
        username += "." + _name_frags[1][0].lower()
    return username
