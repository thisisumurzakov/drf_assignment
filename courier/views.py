from datetime import datetime

from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser

from .models import Courier, Order
from .serializers import CourierSerializer, OrderSerializer

class CView(generics.ListAPIView):
    queryset = Courier.objects.all()
    serializer_class = CourierSerializer

class CourierPostView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        serializer = CourierSerializer(data=request.data['data'], many=True)
        ids = []
        for id in request.data['data']:
            ids.append({'id': id['courier_id']})

        if serializer.is_valid():
            serializer.save()
            return Response(status=201, data={'couriers': ids})
        return Response(status=400, data={"validation_error": {'couriers': ids}})


class CourierPatchGetView(APIView):
    def get_object(self, pk):
        return Courier.objects.get(id=pk)

    def patch(self, request, pk):
        courier_object = self.get_object(pk)
        serializer = CourierSerializer(courier_object, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=201, data=serializer.data)
        return Response(status=400, data="wrong parameters")

    def get(self, request, pk):
        courier = get_object_or_404(Courier, pk=pk)
        times = []
        for region in courier.regions:
            orders_region = Order.objects.filter(courier_field=courier, region=region)
            if orders_region:
                time = 0
                count = 0
                for order in orders_region:
                    if order.time:
                        time += int(order.time)
                        count += 1
                try:
                    time /= count
                    times.append(time)
                except ZeroDivisionError:
                    pass
        if times:
            time = min(times)
            rating = (3600 - min(time, 3600)) / (3600) * 5

            orders = Order.objects.filter(courier_field=courier)
            type = {'foot': 2, 'bike': 5, 'car': 9}
            sum = 0
            for order in orders:
                if order.complete_time:
                    sum += 500*type[courier.courier_type]
            return Response({'courier_id': courier.id, 'courier_type': courier.courier_type, 'regions': courier.regions,
                            'working_hours': courier.working_hours, 'rating': rating, 'earnings': sum})
        return Response({'courier_id': courier.id, 'courier_type': courier.courier_type, 'regions': courier.regions,
                         'working_hours': courier.working_hours})

class OrderPostView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        serializer = OrderSerializer(data = request.data['data'], many=True)
        ids = []
        for id in request.data['data']:
            ids.append({'id': id['order_id']})

        if serializer.is_valid():
            serializer.save()
            return Response(status=201, data={'orders': ids})
        return Response(status=400, data={"validation_error": {'orders': ids}})

def check_hours(courier_hours, order_hours):
    for courier_hour in courier_hours:
        for order_hour in order_hours:
            c_part1 = datetime.strptime(courier_hour[0:5], '%H:%M')
            c_part2 = datetime.strptime(courier_hour[6:11], '%H:%M')
            o_part1 = datetime.strptime(order_hour[0:5], '%H:%M')
            o_part2 = datetime.strptime(courier_hour[6:11], '%H:%M')
            if c_part1 <= o_part1 and c_part2 >= o_part2:
                return True
    return False

class OrderAssignView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        courier = get_object_or_404(Courier, pk=request.data["courier_id"])
        serilizer = CourierSerializer(courier)
        types = {'foot': 10, 'bike': 15, 'car': 50}
        courier_type = serilizer.data["courier_type"]
        regions = serilizer.data["regions"]
        courier_hours = serilizer.data["working_hours"]
        courier_weight = 0
        orders = []
        for region in regions :
            order = Order.objects.filter(region=region, courier_field=None, complete_time=None)
            if order:
                for i in range(0, order.count()):
                    order_hours = order[i].delivery_hours
                    if check_hours(courier_hours, order_hours):
                        if courier_weight+order[i].weight <= types[courier_type]:
                            courier_weight += order[i].weight
                            order[i].courier_field = courier
                            order[i].assign_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            orders.append({'id': order[i].id})
                            order[i].save()
        if orders:
            return Response({'orders': orders, 'assign_time': datetime.now()})
        return Response({'orders': orders})

class OrderCompleteView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        order = get_object_or_404(Order, pk=request.data["order_id"])
        orders = Order.objects.filter(courier_field=order.courier_field, assign_time=order.assign_time)
        complete_times = []
        for other_order in orders:
            if other_order.complete_time:
                complete_times.append(other_order.complete_time.replace(tzinfo=None))
        if complete_times:
            assign = max(complete_times)
        else:
            assign = order.assign_time.replace(tzinfo=None)

        order.complete_time = datetime.strptime(request.data["complete_time"], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=None)
        order.time = int((order.complete_time - assign).total_seconds())
        order.save()
        return Response({'order_id': order.id})

"""{
"data": [
{
"courier_id": 1,
"type": "foot",
"regions": [1, 12, 22],
"hours": ["11:35-14:05", "09:00-11:00"]
},
{
"courier_id": 2,
"type": "bike",
"regions": [22],
"hours": ["09:00-18:00"]
},
{
"courier_id": 3,
"type": "car",
"regions": [12, 22, 23, 33],
"hours": []
}
]
}"""