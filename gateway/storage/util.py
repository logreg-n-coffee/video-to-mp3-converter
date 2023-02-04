import pika
import json


def upload(f, fs, channel, access):
    try:
        # put a file into the mongodb
        fid = fs.put(f)
    except Exception as err:
        return "internal server error", 500

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    try:
        # rabbitmq
        channel.basic_publish(
            exchange="",  # default exchange - routing key is the queue name
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )

    except:
        # if there is no message received remove the file
        fs.delete(fid)
        return "internal server error", 500
