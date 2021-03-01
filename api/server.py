'''import falcon, argparse, json

from wsgiref.simple_server import make_server

from company_metrics_api import CompanyMetricsResource

from config import init_config

api = application = falcon.API()


class VersionResource(object):
    def on_get(self, req, resp):
        resp.body = '{"version": "0.0.1"}'

version_res = VersionResource()
api.add_route('/version', version_res)


company_metrics_res = CompanyMetricsResource()
api.add_route('/metrics/{company_id}', company_metrics_res)


if __name__ == '__main__':
    with make_server('', 8080, api) as httpd:
        parser = argparse.ArgumentParser(description='Financial app http server')
        parser.add_argument('-c','--config_file_path', help='Absolute config file path', required=True)
        args = vars(parser.parse_args())

        try:
            with open(args['config_file_path'], 'r') as f:
                file_content_raw = f.read()
                config_json_content = json.loads(file_content_raw)
                init_config(config_json_content)
                

        except Exception as gen_ex:
            print(str(gen_ex))

        print('Serving on port 8080...')

        # Serve until process is killed
        httpd.serve_forever()'''

import uvicorn, argparse, json

from fastapi import Depends, FastAPI

from config import init_config

import api.routers.company_metric_api as company_metric_api

app = FastAPI()

app.include_router(company_metric_api.router)

@app.get("/version")
async def root():
    return {"version": "0.0.1"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Financial app http server')
    parser.add_argument('-c','--config_file_path', help='Absolute config file path', required=True)
    args = vars(parser.parse_args())

    try:
        with open(args['config_file_path'], 'r') as f:
            file_content_raw = f.read()
            config_json_content = json.loads(file_content_raw)
            init_config(config_json_content)
            

    except Exception as gen_ex:
        print(str(gen_ex))
    
    uvicorn.run(app, host="0.0.0.0", port=8000)