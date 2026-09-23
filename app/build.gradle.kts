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
    implementation(libs.navigation.fragment)
    implementation(libs.navigation.ui)
    implementation(libs.material)

    // Import the BoM for the Firebase platform
    implementation(platform(libs.firebase.bom))
    // Add the dependencies for the Firebase AI Logic and App Check libraries
    // When using the BoM, you don't specify versions in Firebase library dependencies
    implementation(libs.firebase.ai)
    implementation(libs.firebase.appcheck.debug)

    // firbase app check 用到了
    implementation(libs.firebase.appcheck.playintegrity)
    // 切换firebase model 用到了
    implementation(libs.google.adk.kotlin.firebase.android)

    // adk
    implementation(libs.google.adk.kotlin.core.android)
    ksp(libs.google.adk.kotlin.processor)

    testImplementation(libs.junit)
    androidTestImplementation(libs.espresso.core)
    androidTestImplementation(libs.ext.junit)
}