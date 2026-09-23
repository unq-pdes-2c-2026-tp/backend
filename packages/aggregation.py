from django.db.models import Func, Model

from packages.models import PackagePurchase, PackageReview


def aggregate_package_purchase(
    dimension_field: str,
    dimension_name: str,
    expression: Func,
    dimension_model: type[Model],
    result_key: str,
) -> list[dict]:
    """
    Args:
        dimension_field (str): el campo en la db desde PackagePurchase por el que agrupamos
        dimension_name (str): el nombre de ese campo en el resultado
        expression (Func): la anotación que vamos a correr
        dimension_model (type[Model]): el modelo al que pertenece la dimension, para mapear los valores
        result_key (str): la key con la que se devuelven resultados

    Returns:
        una lista de diccionarios donde una key es 'result' y la otra es dimension_name
    """
    return aggregate(
        base_model=PackagePurchase,
        dimension_field=dimension_field,
        dimension_name=dimension_name,
        expression=expression,
        dimension_model=dimension_model,
        result_key=result_key,
    )


def aggregate_package_review(
    dimension_field: str,
    dimension_name: str,
    expression: Func,
    dimension_model: type[Model],
    result_key: str,
) -> list[dict]:
    """
    Args:
        dimension_field (str): el campo en la db desde PackageReview por el que agrupamos
        dimension_name (str): el nombre de ese campo en el resultado
        expression (Func): la anotación que vamos a correr
        dimension_model (type[Model]): el modelo al que pertenece la dimension, para mapear los valores
        result_key (str): la key con la que se devuelven resultados

    Returns:
        una lista de diccionarios donde una key es 'result' y la otra es dimension_name
    """
    return aggregate(
        base_model=PackageReview,
        dimension_field=dimension_field,
        dimension_name=dimension_name,
        expression=expression,
        dimension_model=dimension_model,
        result_key=result_key,
    )


def aggregate(
    base_model: type[Model],
    dimension_field: str,
    dimension_name: str,
    expression: Func,
    dimension_model: type[Model],
    result_key: str,
) -> list[dict]:
    """
    Args:
        base_model: (type[Model]): modelo desde el que se parque la agregación
        dimension_field (str): el campo en la db desde PackagePurchase por el que agrupamos
        dimension_name (str): el nombre de ese campo en el resultado
        expression (Func): la anotación que vamos a correr
        dimension_model (type[Model]): el modelo al que pertenece la dimension, para mapear los valores
        result_key (str): la key con la que se devuelven resultados

    Returns:
        una lista de diccionarios donde una key es 'result' y la otra es dimension_name
    """
    top_results = (
        base_model.objects.values(dimension_field)
        .annotate(result=expression)
        .order_by("-result")[:5]
    )

    results: list[dict] = []
    dimension_ids = [result[dimension_field] for result in top_results]

    city_by_id = dimension_model.objects.filter(id__in=dimension_ids).in_bulk()

    for top_result in top_results:
        results.append(
            {
                dimension_name: city_by_id[top_result[dimension_field]],
                result_key: top_result["result"],
            }
        )

    return results
