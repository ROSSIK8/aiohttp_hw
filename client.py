import aiohttp
import asyncio


async def main():
    async with aiohttp.ClientSession() as session:
        response = await session.post('http://127.0.0.1:8080/ad',
                                      json={
                                          'title': 'Продоётся телефон',
                                          'description': 'Топовый телефон за 18000 руб',
                                          'owner': 'Владелец'
                                      })

        print(response.status)
        print(await response.json())

        response = await session.patch('http://127.0.0.1:8080/ad/1',
                                      json={
                                          'title': 'Продоётся телевизор',
                                          'description': 'Топовый телевизор за 38000 руб',
                                          'owner': 'Владелец'
                                      })

        print(response.status)
        print(await response.json())

        response = await session.get('http://127.0.0.1:8080/ad/1')

        print(response.status)
        print(await response.json())
        #
        response = await session.delete('http://127.0.0.1:8080/ad/1')

        print(response.status)
        print(await response.json())





asyncio.run(main())

