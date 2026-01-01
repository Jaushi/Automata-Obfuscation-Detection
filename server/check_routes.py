from app import app

print('Registered routes:')
for rule in app.url_map.iter_rules():
    print(f'{rule.endpoint:40s} {rule.rule}')
