import json
from aiohttp import web
from models import engine
from models import Ad, Base, Session


app = web.Application()


async def orm_context(app: web.Application):
    print("START")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print("SHUT DOWN")


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request['session'] = session
        response = await handler(request)
        return response


async def get_ad(ad_id: int, session: Session):
    ad = await session.get(Ad, ad_id)
    if ad is None:
        raise web.HTTPNotFound(
            text=json.dumps(
                {
                    'error': 'Not found'
                }
            ),
            content_type='application/json'
        )
    return ad


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)


class AdView(web.View):

    @property
    def session(self) -> Session:
        return self.request['session']

    @property
    def ad_id(self) -> int:
        return int(self.request.match_info['ad_id'])

    async def get(self):
        ad = await get_ad(self.ad_id, self.session)
        return web.json_response({
            'id': ad.id,
            'title': ad.title,
            'description': ad.description
        })

    async def post(self):
        json_data = await self.request.json()
        ad = Ad(**json_data)
        self.session.add(ad)
        await self.session.commit()

        return web.json_response({
            'id': ad.id
        })

    async def patch(self):
        json_data = await self.request.json()
        ad = await get_ad(self.ad_id, self.session)
        for field, value in json_data.items():
            setattr(ad, field, value)

        self.session.add(ad)
        await self.session.commit()

        return web.json_response({
            'id': ad.id
        })

    async def delete(self):
        ad = await get_ad(self.ad_id, self.session)
        await self.session.delete(ad)
        await self.session.commit()
        return web.json_response(
            {
                'status': 'deleted'
            }
        )


app.add_routes([
    web.post('/ad', AdView),
    web.get('/ad/{ad_id}', AdView),
    web.patch('/ad/{ad_id}', AdView),
    web.delete('/ad/{ad_id}', AdView)

])

web.run_app(app)