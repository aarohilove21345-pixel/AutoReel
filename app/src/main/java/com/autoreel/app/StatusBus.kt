package com.autoreel.app

import androidx.lifecycle.MutableLiveData

object StatusBus {
    val log = MutableLiveData<String>()
    val state = MutableLiveData<String>()

    fun post(message: String) {
        log.postValue(message)
    }

    fun setState(s: String) {
        state.postValue(s)
    }
}
