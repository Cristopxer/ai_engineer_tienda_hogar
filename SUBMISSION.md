## Arquitectura propuesta y justificación
[Diagrama simple (ASCII, Mermaid, o descripción por componentes) de tu
solución. Explica por qué elegiste este diseño y qué trade-offs hiciste
dado el límite de tiempo.]

## Decisiones técnicas de RAG
- Chunking: ¿aplicaste chunking a estos documentos? ¿Por qué o por qué no,
 considerando su tamaño? ¿Cómo lo harías si este corpus creciera a miles
 de documentos?
- Embeddings: ¿qué modelo de embeddings usaste y por qué?
- Threshold de recuperación: ¿qué score/umbral de similitud (o top-k)
 usaste para decidir si un documento es lo bastante relevante para usarse
 en la respuesta? ¿Qué pasa en tu solución si ningún documento supera
 ese umbral?

## Pruebas automatizadas
[Qué casos cubren tus tests y el comando exacto para correrlos.]

## Cómo mapearías esto a producción
[Este prototipo es local. En Grupo Mariposa, los agentes corren sobre
Microsoft Foundry, con RAG sobre Databricks/Unity Catalog, Apigee como API
gateway, y Kafka para eventos asíncronos. Describe brevemente qué cambiaría
de tu arquitectura para llevarla a ese stack.]

## Limitaciones conocidas
[¿Qué NO funciona bien en tu solución, o qué no alcanzaste a probar?]

## Tiempo invertido
[Horas aproximadas]