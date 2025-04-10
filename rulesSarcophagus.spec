define {
    SOME_ID: uint256 = 123;
    sarcoId: uint256 = 123;
    REWRAP_TIME: uint256 = 1 days;
    payment: uint256 = 1 ether;

    archaeologist: address = address(0x111);
    embalmer: address = address(0x222);
    attacker: address = address(0xabc);
    nonArchaeologist: address = address(0x123);
}

rule onlyAuthorizedArchaeologistCanAccuse() {
    // Garante que apenas um arqueólogo autorizado pode fazer uma acusação.
    expect revert by nonArchaeologist;
    Sarcophagus.accuse(nonArchaeologist, SOME_ID);
}

rule cannotAccuseAfterRewrap() {
    // Garante que não é possível acusar após o tempo de rewrap.
    // Avança o tempo além do REWRAP_TIME e espera que a acusação reverta.
    advance_time(REWRAP_TIME + 1);
    expect revert by archaeologist;
    Sarcophagus.accuse(archaeologist, sarcoId);
}

rule sarcophagusInactiveAfterBury() {
    // Verifica que após enterrar (bury) um sarcófago, ele não deve estar ativo.
    Sarcophagus.bury(sarcoId);
    assert !Sarcophagus.isActive(sarcoId);
}

rule onlyEmbalmerCanRewrap() {
    // Garante que apenas o embalsamador pode fazer o rewrap.
    // Qualquer outra conta deve reverter ao tentar.
    expect revert by attacker;
    Sarcophagus.rewrap(sarcoId);
}

rule unwrapInFutureOnly() {
    // Impede que o rewrap seja feito com um tempo no passado.
    // Tenta rewrap com tempo menor que o atual e espera que reverta.
    uint256 pastTime = block.timestamp - 1;
    expect revert by embalmer;
    Sarcophagus.rewrap(sarcoId, pastTime);
}

rule archaeologistNotPaidTwice() {
    // Garante que o arqueólogo só recebe o pagamento uma vez.
    // Mesmo após chamar `claimPayment` duas vezes, o saldo só deve aumentar uma vez.
    uint256 balanceBefore = archaeologist.balance;
    Sarcophagus.claimPayment(sarcoId);
    Sarcophagus.claimPayment(sarcoId);
    assert archaeologist.balance == balanceBefore + payment;
}

rule createSarcophagusEmitsEvent() {
    // Verifica que o evento `SarcophagusCreated` é emitido corretamente na criação.
    expect emit SarcophagusCreated(sarcoId, embalmer, archaeologist);
    Sarcophagus.create(sarcoId, embalmer, archaeologist);
}

rule archaeologistSlashedOnAccusation() {
    // Garante que o arqueólogo perde parte do seu bond (depósito) ao ser acusado.
    uint256 bondBefore = Sarcophagus.bonds(archaeologist);
    Sarcophagus.accuse(archaeologist, sarcoId);
    assert Sarcophagus.bonds(archaeologist) < bondBefore;
}

rule onlyActiveArchaeologistCanBeSelected() {
    // Impede que arqueólogos inativos sejam selecionados para um novo sarcófago.
    Sarcophagus.setInactive(archaeologist);
    expect revert by embalmer;
    Sarcophagus.create(sarcoId, embalmer, archaeologist);
}

rule rewrapUpdatesUnwrapTime() {
    // Garante que o tempo de unwrap é corretamente atualizado após um rewrap.
    uint256 newTime = block.timestamp + 1 days;
    Sarcophagus.rewrap(sarcoId, newTime);
    assert Sarcophagus.unwrapTime(sarcoId) == newTime;
}

invariant archaeologistNotPaidIfInactive() {
    // Invariante: arqueólogo não deve receber pagamento se estiver inativo.
    if (!Sarcophagus.isActive(sarcoId)) {
        assert Sarcophagus.payments(archaeologist, sarcoId) == 0;
    }
}
