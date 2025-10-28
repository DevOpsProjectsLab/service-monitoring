from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import random

app = Flask(__name__)

REQUEST_COUNT = Counter(
    'app_requests_total',
    'Total de requisições HTTP recebidas',
    ['method', 'endpoint']
)

REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Tempo de resposta por endpoint',
    ['endpoint']
)

ACTIVE_USERS = Gauge(
    'app_active_users',
    'Número de usuários ativos simulados'
)

ORDERS_TOTAL = Counter(
    'orders_total',
    'Total de pedidos processados'
)

ORDER_PROCESSING_TIME = Histogram(
    'order_processing_time_seconds',
    'Tempo de processamento por pedido'
)

ORDER_VALUE_TOTAL = Counter(
    'order_value_total',
    'Valor total acumulado dos pedidos'
)

AVG_ORDER_VALUE = Gauge(
    'avg_order_value',
    'Valor médio dos pedidos (ticket médio)'
)

@app.route('/')
def index():
    REQUEST_COUNT.labels(method='GET', endpoint='/').inc()
    with REQUEST_LATENCY.labels(endpoint='/').time():
        return jsonify({"message": "🏁 Service Monitoring API - Instrumented with Prometheus"})


@app.route('/users/<int:qtd>')
def users(qtd):
    REQUEST_COUNT.labels(method='GET', endpoint='/users').inc()
    ACTIVE_USERS.set(qtd)
    return jsonify({"active_users": qtd})


@app.route('/order', methods=['POST'])
def create_order():
    """Simula o processamento de um pedido de compra"""
    REQUEST_COUNT.labels(method='POST', endpoint='/order').inc()

    with REQUEST_LATENCY.labels(endpoint='/order').time():
        value = random.uniform(10, 200)
        start_time = time.time()
        time.sleep(random.uniform(0.2, 1.0))  
        duration = time.time() - start_time

        ORDERS_TOTAL.inc()
        ORDER_VALUE_TOTAL.inc(value)
        ORDER_PROCESSING_TIME.observe(duration)

        avg_value = ORDER_VALUE_TOTAL._value.get() / ORDERS_TOTAL._value.get()
        AVG_ORDER_VALUE.set(avg_value)

        return jsonify({
            "status": "success",
            "order_value": round(value, 2),
            "processing_time": round(duration, 2),
            "avg_order_value": round(avg_value, 2)
        })


@app.route('/metrics')
def metrics():
    """Endpoint Prometheus"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
