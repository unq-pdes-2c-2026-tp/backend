Feature: agency permissions
  description
    evalua los permisos sobre las agencias: los admins pueden crear, modificar y borrar, mientras
  que el resto de los usuarios solo pueden leer

  Scenario: un usuario final intenta crear una agencia
    Given un usuario final
    When intenta crear una agencia
     Then un error de permisos insuficientes es devuelto.
