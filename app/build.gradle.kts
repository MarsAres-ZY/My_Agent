plugins {
    id("com.android.application")
    id("com.google.devtools.ksp") version "2.3.6"
    id("com.google.gms.google-services")
}

android {
    namespace = "com.example.agent"
    compileSdk {
        version = release(37)
    }

    defaultConfig {
        applicationId = "com.example.agent"
        minSdk = 34
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            optimization {
                enable = false
            }
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }

    buildFeatures {
        viewBinding = true
    }

    packaging {
        resources {
            excludes += setOf(
                "META-INF/INDEX.LIST",
                "META-INF/DEPENDENCIES",
            )
        }
    }
}

dependencies {
    implementation(libs.activity.ktx)
    implementation(libs.appcompat)
    implementation(libs.constraintlayout)
    implementation(libs.firebase.appcheck.playintegrity)
    implementation(libs.material)

    implementation(platform("com.google.firebase:firebase-bom:34.18.0"))
    implementation("com.google.firebase:firebase-ai")
    implementation("com.google.firebase:firebase-appcheck-debug")
    implementation("com.google.adk:google-adk-kotlin-firebase-android:1.0.0")

    implementation(libs.google.adk.kotlin.core.android)
    implementation(libs.navigation.fragment)
    implementation(libs.navigation.ui)
    ksp(libs.google.adk.kotlin.processor)

    testImplementation(libs.junit)
    androidTestImplementation(libs.espresso.core)
    androidTestImplementation(libs.ext.junit)
}