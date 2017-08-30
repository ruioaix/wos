import os

userid = 1
users = {}
orgid = 1
orgs = {}
rela = {}

for fn in os.listdir('op'):
    with open(os.path.join('op', fn)) as fo:
        for line in fo:
            parts = line.strip().split(';')
            name = parts[0]
            add = parts[1]
            org = parts[2]
            frq = parts[3]
            user = (name, add)
            if user not in users:
                users[user] = userid
                userid += 1
            if org not in orgs:
                orgs[org] = orgid
                orgid += 1
            if users[user] not in rela:
                rela[users[user]] = {}
            rela[users[user]][orgs[org]] = frq

with open('users', 'w') as fo:
    for user in users:
        name, add = user
        fo.write('{};{};{}\n'.format(name, add, users[user]))

with open('orgs', 'w') as fo:
    for org in orgs:
        fo.write('{};{}\n'.format(org, orgs[org]))

with open('rela', 'w') as fo:
    for user in rela:
        for org in rela[user]:
            fo.write('{};{};{}\n'.format(user, org, rela[user][org]))
