Feature: agency permissions
  description
    evalua los permisos sobre las agencias: los admins pueden crear, modificar y borrar, mientras
  que el resto de los usuarios solo pueden leer

  Scenario Outline: ejemplo
    Given un <usuario>
    Given una agencia
      When intenta <accion> una agencia
     Then <result>
    Examples: acciones sobre agencias
     | usuario                   | accion | result |
     | usuario final             | crear  | un error de permisos insuficientes es devuelto  |
     | usuario agencia           | crear  | un error de permisos insuficientes es devuelto  |
     | usuario administrador     | crear  | la agencia es creada correctamente  |
     | usuario final             | modificar  | un error de permisos insuficientes es devuelto  |
     | usuario agencia           | modificar  | un error de permisos insuficientes es devuelto  |
     | usuario administrador     | modificar  | la agencia es modificada correctamente  |
