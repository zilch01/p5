from flask import Flask, render_template, request, jsonify
from redis import Redis, RedisError
import hashlib
import requests


app = Flask(__name__)
redis = Redis(host='redis', port=6379)

@app.route('/')
def hello_world():
  return 'Hello from Flask!'

@app.route('/redis/')
def hello():
    count = redis.incr('hits')
    return 'Hello World! I have been seen {} times.\n'.format(count)

@app.route('/factorial/<int:x>')
def factorial(x,y=1):
        inp = x #fixes '0' bug
        while x > 0:
                y=y*x
                x=x-1
        return jsonify( input = inp, output = y )

@app.route('/fibonacci/<int:x>')
def fibonacci(x):
        fibList=[0,1] # will become full fibonacci list up to x

        if x >= 4: # works for x=4+
                for i in range(2,x+1):
                        fibList.append(fibList[i-1]+fibList[i-2])

                #less than or equal to
                fibListLTE=[]
                for i in fibList:
                        if i <= x:
                                fibListLTE.append(i)
        else: # works for x=1 through 3
                for i in range(2,x+2):
                        fibList.append(fibList[i-1]+fibList[i-2])

                #less than or equal to
                fibListLTE=[]
                for i in fibList:
                        if i <= x:
                                fibListLTE.append(i)

        return jsonify( input = x, output = fibListLTE )


@app.route('/md5/<inputString>')
def md5(inputString):
        m = hashlib.md5()
        m.update(inputString)
        return jsonify ( input = inputString, output = m.hexdigest() )

@app.route('/is-prime/<int:x>')
def isPrime(x):
        sqrt = x**0.5
        sqrt = int(sqrt) #truncate float into an integer

        i = 2
        isPrime = True

        #1 is not a prime
        if x==1:
                isPrime = False

        # https://en.wikipedia.org/wiki/Primality_test says only test from 0 to sqrt
        while i <= sqrt:
                if x % i == 0:
                        isPrime = False
                i=i+1

        return jsonify( input = x, output = isPrime )

@app.route('/slack-alert/<input_string>')
def slacker(input_string):

        SLACK_WEBHOOK = 'https://hooks.slack.com/services/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'

        data = { 'text': input_string }
        resp = requests.post(SLACK_WEBHOOK, json=data)

        if resp.status_code == 200:
                output_val = True
        else:
                output_val = False

        return jsonify ( input = input_string, output = output_val )

@app.route('/kv-record/<string:key>', methods=['POST'])
def kv_create(key):
    input = key
    output = False
    err_msg = None
    try:
        # first ensure this key does NOT exist (POST == create only)
        value = redis.get(key)
        if not value == None: 
            err_msg = "Cannot create new record: key already exists."
        else:
            # ok, this is a new key. let's create it
            payload = request.get_json()
            create_red = redis.set(key, payload['value'])
            if create_red == False:
                err_msg = "ERROR: There was a problem creating the value in Redis."
            else:
                output = True
                input = payload
    except RedisError:
        err_msg = "Cannot connect to redis."

    return jsonify(
        input=input,
        output=output,
        error=err_msg
    )

@app.route('/kv-record/<string:key>', methods=['PUT'])
def kv_update(key):
    input = key
    output = False
    err_msg = None
    try:
        # first check to see if this key even exists (PUT == update only)
        value = redis.get(key)
        if value == None: 
            err_msg = "Cannot update: key does not exist."
        else:
            # ok, key exists. now update it
            payload = request.get_json()
            update_red = redis.set(key, payload['value'])
            if update_red == False:
                err_msg = "ERROR: There was a problem updating the value in Redis."
            else:
                output = True
                input = payload
    except RedisError:
        err_msg = "Cannot connect to redis."

    return jsonify(
        input=input,
        output=output,
        error=err_msg
    )

@app.route('/kv-retrieve/<string:key>')
def kv_retrieve(key):
    output = False
    err_msg = None
    try:
        value = redis.get(key)
        if value == None:
            err_msg = "Key does not exist."
        else:
            output = value
    except RedisError:
        err_msg = "Cannot connect to redis."

    return jsonify(
        input=key,
        output=output,
        error=err_msg
    )

if __name__ == '__main__':
  app.run(debug=True,host='0.0.0.0')
