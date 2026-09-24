package com.example.agent;

import androidx.annotation.NonNull;

import com.google.adk.kt.interop.BasePublisherModel;
import com.google.adk.kt.models.LlmRequest;
import com.google.adk.kt.models.LlmResponse;

import org.reactivestreams.Publisher;


public class LlmModel extends BasePublisherModel {
    public LlmModel(@NonNull String name) {
        super(name);
    }

    @NonNull
    @Override
    protected Publisher<LlmResponse> generateContentJava(@NonNull LlmRequest llmRequest, boolean b) {
        return null;
    }
}
