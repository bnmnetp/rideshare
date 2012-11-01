def createContext():
    cd = {}
    cd['logout_url'] = users.create_logout_url("/")
    me = users.get_current_user()
    if me:
        cd['nickname'] = me.nickname()
    return cd
