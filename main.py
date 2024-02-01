import docker
from flask import Flask, render_template

app = Flask(__name__)


class DockerInstance:
    def __init__(self, base_url='unix://var/run/docker.sock'):
        self.client = docker.client.APIClient(base_url=base_url)
    
    def containers(self):
        containers = []
        for c in self.client.containers():
            containers.append(c.get('Labels'))
        return containers
    
    def services(self):
        services = []
        for c in self.containers():
            services.append(c.get('com.docker.compose.service'))
        return services
    
    def service_status(self):
        service_status = {}
        for service in self.services():
            service_status[service] = self.client.inspect_container(service).get('State').get('Health')
        return service_status


class Server:
    def __init__(self, app_inst, host='localhost', port=5000, debug=False):
        self.app_inst = app_inst
        self.host = host
        self.port = port
        self.debug = debug
    
    def run(self):
        self.app_inst.run(host=f'{self.host}', port=f'{self.port}', debug=self.debug)


@app.route('/')
def index():
    docker_instance = DockerInstance()
    if docker_instance.service_status() is None:
        return 'No services found', 404
    return render_template('index.html', status_data=docker_instance.service_status()), 200


if __name__ == '__main__':
    server = Server(app_inst=app, host='localhost', port=5000, debug=True)
    server.run()
