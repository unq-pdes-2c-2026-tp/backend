Feature: user sign up rules
  description
    evalua las reglas sobre la creación de usuarios

  Scenario Outline: ejemplo
    Given un payload de <usuario>
    Given una agencia
      When intenta crear una <cuenta>
     Then <result>
    Examples: casos de creación de cuenta
     | usuario                   | cuenta | result |
     | usuario final             | cuenta sin agencia  | el usuario es creado y la agencia es nula |
     | usuario agencia           | cuenta sin agencia  | un error de validacion es devuelto |
     | usuario administrador     | cuenta sin agencia  | el usuario es creado y la agencia es nula |
     | usuario final             | cuenta con agencia  | el usuario es creado y la agencia es nula |
     | usuario agencia           | cuenta con agencia  | el usuario es creado y la agencia esta asociada |
     | usuario administrador     | cuenta con agencia  | el usuario es creado y la agencia es nula |
