WMTS_GET_CAPABILITIES_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<Capabilities version="1.0.0" xmlns="http://www.opengis.net/wmts/1.0" xmlns:ows="http://www.opengis.net/ows/1.1"
              xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xmlns:gml="http://www.opengis.net/gml"
              xsi:schemaLocation="http://schemas.opengis.net/wmts/1.0/wmtsGetCapabilities_response.xsd">
  <ows:ServiceIdentification> </ows:ServiceIdentification>
  <ows:ServiceProvider> </ows:ServiceProvider>
  <ows:OperationsMetadata>
    <ows:Operation name="GetTile">
      <ows:DCP>
        <ows:HTTP><ows:Get xlink:href="{{wmts_gettile}}" /></ows:HTTP>
      </ows:DCP>
    </ows:Operation>
  </ows:OperationsMetadata>
  <!-- <ServiceMetadataURL xlink:href="" /> -->
  <Contents>

    {% for layer in layers %}
    <Layer>
      <ows:Title>{{layer['name']}}</ows:Title>
      <ows:Identifier>{{layer['name']}}</ows:Identifier>
      <Style isDefault="true">
        <ows:Identifier>default</ows:Identifier>
      </Style>
      <Format>{{layer['format']}}</Format>
      <Dimension>
        <ows:Identifier>{{layer["dimension_key"]}}</ows:Identifier>
        <Default>{{layer["dimension_default"]}}</Default>
        {% for value in layers["dimension_values"] %}
        <Value>{{value}}</Value>
        {% endfor %}
      </Dimension>
      <ResourceURL format="{{layer['mime_type']}}" resourceType="tile"
                   template="{{wmts_gettile}}/1.0.0/{{layer['name']}}/{style}/{{'{'}}{{layer['dimension_key']}}{{'}'}}/{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}.{{layer['extension']}}" />
      <TileMatrixSetLink>
        <TileMatrixSet>{{layer["metadata_matrix_set"]}}</TileMatrixSet>
      </TileMatrixSetLink>
    </Layer>
    {% endfor %}

    {% for key, matrix_set in matrix_sets.items() %}
    <TileMatrixSet>
      <ows:Identifier>{{key}}</ows:Identifier>
      <ows:SupportedCRS>urn:ogc:def:crs:{{matrix_set["crs"]}}</ows:SupportedCRS>
      {% for matrix in matrix_set["matrices"] %}
      <TileMatrix>
        <ows:Identifier>{{matrix["id"]}}</ows:Identifier>
        <ScaleDenominator>{{matrix["scale"]}}</ScaleDenominator> <!-- resolution: {{matrix["resolution"]}} -->
        <TopLeftCorner>{{matrix["topleft"]}}</TopLeftCorner>
        <TileWidth>{{matrix["tilewidth"]}}</TileWidth>
        <TileHeight>{{matrix["tileheight"]}}</TileHeight>
        <MatrixWidth>{{matrix["matrixwidth"]}}</MatrixWidth>
        <MatrixHeight>{{matrix["matrixheight"]}}</MatrixHeight>
      </TileMatrix>
      {% endfor %}
    </TileMatrixSet>
    {% endfor %}
  </Contents>
</Capabilities>
"""
