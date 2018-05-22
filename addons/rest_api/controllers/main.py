# Part of Flectra. See LICENSE file for full copyright and licensing details.

import functools
import hashlib
import os
import werkzeug.wrappers
import ast
try:
    import simplejson as json
except ImportError:
    import json
import flectra
from flectra import http
from flectra.http import request
from flectra import fields
from ..rest_exception import *

_logger = logging.getLogger(__name__)


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode("ASCII")
        return json.JSONEncoder.default(self, obj)


def eval_json_to_data(modelname, json_data, create=True):
    Model = request.env[modelname]
    model_fiels = Model._fields
    field_name = [name for name, field in Model._fields.items()]
    values = {}
    for field in json_data:
        if field not in field_name:
            continue
        if field not in field_name:
            continue
        val = json_data[field]
        if not isinstance(val, list):
            values[field] = val
        else:
            values[field] = []
            if not create and isinstance(model_fiels[field], fields.Many2many):
                values[field].append((5,))
            for res in val:
                recored = {}
                for f in res:
                    recored[f] = res[f]
                if isinstance(model_fiels[field], fields.Many2many):
                    values[field].append((4, recored['id']))

                elif isinstance(model_fiels[field], flectra.fields.One2many):
                    if create:
                        values[field].append((0, 0, recored))
                    else:
                        if 'id' in recored:
                            id = recored['id']
                            del recored['id']
                            values[field].append((1, id, recored)) if len(recored) else values[field].append((2, id))
                        else:
                            values[field].append((0, 0, recored))
    return values


def object_read(modelname, default_domain, status_code,
                             post={}):
    json_data = post
    domain = default_domain or []
    field = []
    offset = 0
    limit = None
    order = None
    if 'filters' in json_data:
        domain += ast.literal_eval(json_data['filters'])
    if 'field' in json_data:
        field += ast.literal_eval(json_data['field'])
    if 'offset' in json_data:
        offset = int(json_data['offset'])
    if 'limit' in json_data:
        limit = int(json_data['limit'])
    if 'order' in json_data:
        order = json_data['order']

    # Search Read object:
    final_data = []
    data = request.env[modelname].search_read(domain, offset=offset, limit=limit, order=order)
    if(data):
        final_data = json.loads(json.dumps(data, cls=JSONEncoder))

        return valid_response(status=status_code,
                              data={
                                  'count': len(data), 'results': final_data
                              })
    else:
        return object_not_found_all(modelname)


def object_read_one(modelname, id, status_code):
    try:
        id = int(id)
    except:
        pass

    if not id:
        return invalid_object_id()
    data = request.env[modelname].search_read(domain=[('id', '=', id)])
    if data:
        final_data = json.loads(json.dumps(data, cls=JSONEncoder))
        return valid_response(status=status_code, data=final_data)
    else:
        return object_not_found(id, modelname)


def object_create_one(modelname, data, status_code):
    vals = data
    try:
        res = request.env[modelname].create(vals)
        flectra_error = ''
    except Exception as e:
        res = None
        flectra_error = e
    if res:
        return valid_response(status_code, {'id': res.id})
    else:
        return no_object_created(flectra_error)


def object_update_one(modelname, id, data, status_code):
    try:
        id = int(id)
    except:
        id = None
    if not id:
        return invalid_object_id()

    vals = data
    try:
        res = request.env[modelname].search([('id', '=', id)])
        if res:
            res.write(vals)
        else:
            return object_not_found(id, modelname)
        flectra_error = ''
    except Exception as e:
        res = None
        flectra_error = e
    if res:
        return valid_response(status_code, 'Record Updated successfully!')
    else:
        return no_object_updated(flectra_error)


def object_delete_one(modelname, id, status_code):
    try:
        id = int(id)
    except:
        id = None
    if not id:
        return invalid_object_id()
    try:
        res = request.env[modelname].search([('id', '=', id)])
        if res:
            res.unlink()
        else:
            return object_not_found(id, modelname)
        flectra_error = ''
    except Exception as e:
        res = None
        flectra_error = e
    if res:
        return valid_response(status_code, 'Record Successfully Deleted!')
    else:
        return no_object_deleted(flectra_error)


def check_valid_token(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        access_token = request.httprequest.headers.get('access_token')
        if not access_token:
            info = "Missing access token in request header!"
            error = 'access_token_not_found'
            _logger.error(info)
            return invalid_response(400, error, info)

        access_token_data = request.env['oauth.access_token'].sudo().search(
            [('token', '=', access_token)], order='id DESC', limit=1)

        if access_token_data._get_access_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_token()

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap


def generate_token(length=40):
    random_data = os.urandom(100)
    hash_gen = hashlib.new('sha512')
    hash_gen.update(random_data)
    return hash_gen.hexdigest()[:length]


# Read OAuth2 constants and setup token store:
db_name = flectra.tools.config.get('db_name')
if not db_name:
    _logger.warning("Warning: To proper setup OAuth - it's necessary to "
                    "set the parameter 'db_name' in flectra config file!")


# List of REST resources in current file:
#   (url prefix)            (method)     (action)
# /api/auth/get_tokens        POST    - Login in flectra and get access tokens
# /api/auth/delete_tokens     POST    - Delete access tokens from token store


# HTTP controller of REST resources:

class ControllerREST(http.Controller):

    # Login in flectra database and get access tokens:
    @http.route('/api/auth/get_tokens', methods=['POST'], type='http',
                auth='none', csrf=False)
    def api_auth_gettokens(self, **post):
        # Convert http data into json:
        db = post['db'] if post.get('db') else None
        username = post['username'] if post.get('username') else None
        password = post['password'] if post.get('password') else None
        # Compare dbname (from HTTP-request vs. flectra config):
        if db and (db != db_name):
            info = "Wrong 'dbname'!"
            error = 'wrong_dbname'
            _logger.error(info)
            return invalid_response(400, error, info)

        # Empty 'db' or 'username' or 'password:
        if not db or not username or not password:
            info = "Empty value of 'db' or 'username' or 'password'!"
            error = 'empty_db_or_username_or_password'
            _logger.error(info)
            return invalid_response(400, error, info)
        # Login in flectra database:
        try:
            request.session.authenticate(db, username, password)
        except:
            # Invalid database:
            info = "Invalid database!"
            error = 'invalid_database'
            _logger.error(info)
            return invalid_response(400, error, info)

        uid = request.session.uid
        # flectra login failed:
        if not uid:
            info = "flectra User authentication failed!"
            error = 'flectra_user_authentication_failed'
            _logger.error(info)
            return invalid_response(401, error, info)

        # Generate tokens
        access_token = request.env['oauth.access_token']._get_access_token(user_id = uid, create = True)

        # Save all tokens in store
        _logger.info("Save OAuth2 tokens of user in store...")

        # Successful response:
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'),
                     ('Pragma', 'no-cache')],
            response=json.dumps({
                'uid': uid,
                'user_context': request.session.get_context() if uid else {},
                'company_id': request.env.user.company_id.id if uid else 'null',
                'access_token': access_token,
                'expires_in': request.env.ref('rest_api.oauth2_access_token_expires_in').sudo().value,
                }),
        )

    # Delete access tokens from token store:
    @http.route('/api/auth/delete_tokens', methods=['POST'], type='http',
                auth='none', csrf=False)
    def api_auth_deletetokens(self, **post):
        # Try convert http data into json:
        access_token = request.httprequest.headers.get('access_token')
        access_token_data = request.env['oauth.access_token'].sudo().search(
            [('token', '=', access_token)], order='id DESC', limit=1)

        if not access_token_data:
            info = "No access token was provided in request!"
            error = 'no_access_token'
            _logger.error(info)
            return invalid_response(400, error, info)
        access_token_data.sudo().unlink()
        # Successful response:
        return valid_response(
            200,
            {}
        )

    @http.route([
        '/api/<model_name>',
        '/api/<model_name>/<id>'
    ], type='http', auth="none", methods=['POST', 'GET', 'PUT', 'DELETE'],
        csrf=False)
    @check_valid_token
    def restapi_access_token(self, model_name=False, id=False, **post):
        Model = request.env['ir.model']
        Model_id = Model.sudo().search([('model', '=', model_name)], limit=1)

        if Model_id:
            if Model_id.rest_api:
                return getattr(self, '%s_data' % (
                    request.httprequest.method).lower())(
                    model_name=model_name, id=id, **post)
            else:
                return rest_api_unavailable(model_name)
        return modal_not_found(model_name)

    def get_data(self, model_name=False, id=False, **post):
        if id:
            return object_read_one(
                modelname=model_name,
                id=id,
                status_code=200,
            )
        return object_read(
            modelname=model_name,
            default_domain=[],
            status_code=200,
            post=post
        )

    def put_data(self, model_name=False, id=False, **post):
        return object_update_one(
            modelname=model_name,
            id=id,
            data=post,
            status_code=200,
        )

    def post_data(self, model_name=False, id=False, **post):
        return object_create_one(
            modelname=model_name,
            data=post,
            status_code=200,
        )

    def delete_data(self, model_name=False, id=False):
        return object_delete_one(
            modelname=model_name,
            id=id,
            status_code=200
        )
