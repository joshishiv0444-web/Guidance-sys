package com.example.aiorb.network

import com.example.aiorb.models.*
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface SafeAssistApi {

    @POST("api/v1/guidance")
    suspend fun getGuidance(@Body request: GuidanceRequest): Response<GuidanceResponse>

    @POST("api/v1/fraud/url")
    suspend fun checkUrl(@Body request: URLRequest): Response<URLResponse>

    @POST("api/v1/fraud/scam")
    suspend fun checkScam(@Body request: ScamRequest): Response<ScamResponse>

    @POST("api/friction")
    suspend fun syncTelemetry(@Body request: List<FrictionPayload>): Response<Any>
}
