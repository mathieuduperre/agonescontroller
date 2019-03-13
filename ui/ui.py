#!/usr/bin/python

from flask import Flask, render_template, request, jsonify
from kubernetes import client, config
import os
import logging


DOMAIN = 'stable.agones.dev'
VERSION = 'v1'
NAMESPACE = os.environ['GUITAR_NAMESPACE'] if 'GUITAR_NAMESPACE' in os.environ else 'agones-system'

app = Flask(__name__)

tcp = 7654
my_app = 'simple-udp'
my_image = 'gcr.io/agones-images/udp-server:0.7'

def create_gs_app(self, app, request_id):
    """

    :param app:
    :type app:
    :param request_id:
    :type request_id:
    :return:
    :rtype:
    """
    # PORTS
    ports = []
    ports.append(client.V1ContainerPort(name="tcp", container_port=tcp, protocol="TCP"))

    logging.debug("Agones container creation string {} {} {} {}".format(my_image, ports, my_app, ''))

    env = []
    my_requests = {'memory': '32Mi', 'cpu': '20m'}
    my_limits = {'memory': '32Mi', 'cpu': '20m'}

    my_resources = client.V1ResourceRequirements(
        requests=my_requests, limits=my_limits
    )

    my_container = client.V1Container(
        name=my_app,
        image=my_image,
        env=env,
        resources=my_resources
    )

    my_kind = {'kind':'GameServer'}



    # The Label will be used as a reference into K8S
    label = 'app-' + str(app.name) + '-' + request_id

    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": label}),
        spec=client.V1PodSpec(containers=[container], host_network=True, restart_policy="Never"))

    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template)

    # Instantiate the deployment object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=label),
        spec=spec)

    self.logger.info("The instance in K8 will be under the label of %s" % label)

    return job


@app.route("/gsadd", methods=['POST'])
def gsadd():
    name = request.form['name'].lower()
    image = request.form['image']
    body = {'kind': 'Guitar', 'spec': {'image': brand, 'review': False}, 'apiVersion': '%s/%s' % (DOMAIN, VERSION), 'metadata': {'name': name, 'namespace': NAMESPACE}}
    crds = client.CustomObjectsApi()
    try:
        crds.create_namespaced_custom_object(DOMAIN, VERSION, NAMESPACE, 'guitars', body)
        result = {'result': 'success'}
        # code = 200
    except Exception as e:
        message = [x.split(':')[1] for x in e.body.split(',') if 'message' in x][0].replace('"', '')
        result = {'result': 'failure', 'reason': message}
        # code = e.status
    response = jsonify(result)
    # response.status_code = code
    return response


@app.route("/gsdelete", methods=['POST'])
def gsdelete():
    name = request.form['name']
    crds = client.CustomObjectsApi()
    try:
        crds.delete_namespaced_custom_object(DOMAIN, VERSION, NAMESPACE, 'guitars', name, client.V1DeleteOptions())
        result = {'result': 'success'}
        # code = 200
    except Exception as e:
        message = [x.split(':')[1] for x in e.body.split(',') if 'message' in x][0].replace('"', '')
        result = {'result': 'failure', 'reason': message}
        # code = e.status
    response = jsonify(result)
    # response.status_code = code
    return response


@app.route("/gsform")
def gsform():
    return render_template("gsform.html", title="Add Your Gameserver")


@app.route("/gslist")
def gslist():
    """
    display gameservers
    """
    crds = client.CustomObjectsApi()
    gs = crds.list_cluster_custom_object(DOMAIN, VERSION, 'gameservers')["items"]
    return render_template("gslist.html", title="Gameservers", gs=gs)


@app.route("/")
def index():
    """
    display gameservers
    """
    return render_template("index.html", title="GameServers")


def run():
    if 'KUBERNETES_PORT' in os.environ:
        # os.environ['KUBERNETES_SERVICE_HOST'] = 'kubernetes'
        config.load_incluster_config()
    else:
        config.load_kube_config()
    app.run(host="0.0.0.0", port=9000)
    run()

if __name__ == '__main__':
    run()
