<template>
  <div class="hand-detection">
    <video
      ref="videoElement"
      class="input-video"
      width="320"
      height="240"
      autoplay
    ></video>
    
    <canvas
      ref="canvasElement"
      class="output-canvas"
      width="320"
      height="240"
    ></canvas>
    
    <div v-if="handClosed" class="alert">截图成功！请拖动到另一设备！</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Hands, HAND_CONNECTIONS } from '@mediapipe/hands'
import { Camera } from '@mediapipe/camera_utils'
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils'

const videoElement = ref(null)
const canvasElement = ref(null)
const handClosed = ref(false)  // 控制提示框显示
let hands = null
let camera = null

// 计算两点之间的距离
function calculateDistance(p1, p2) {
  const dx = p1.x - p2.x
  const dy = p1.y - p2.y
  return Math.sqrt(dx * dx + dy * dy)
}

// 判断手指是否闭合
function checkHandClosed(landmarks) {
  const thumbTip = landmarks[4]  // 拇指末端
  const indexTip = landmarks[8]  // 食指末端
  
  const distance = calculateDistance(thumbTip, indexTip)
  const threshold = 0.05  // 设置一个阈值，阈值越小越容易判断为闭合

  if (distance < threshold) {
    return true
  }
  return false
}

// 处理 MediaPipe 结果并绘制手部标记
function onResults(results) {
  const canvasCtx = canvasElement.value.getContext('2d', { alpha: false })
  
  requestAnimationFrame(() => {
    canvasCtx.save()
    canvasCtx.clearRect(0, 0, canvasElement.value.width, canvasElement.value.height)

    if (results.multiHandLandmarks) {
      let handClosedDetected = false  // 用于记录是否有手指闭合的标志

      for (const landmarks of results.multiHandLandmarks) {
        drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, {
          color: '#00FF00',
          lineWidth: 2
        })
        drawLandmarks(canvasCtx, landmarks, {
          color: '#FF0000',
          lineWidth: 1,
          radius: 3
        })

        // 检测手指是否闭合
        if (checkHandClosed(landmarks)) {
          handClosedDetected = true  // 如果手闭合，设置为 true
        }
      }

      // 如果手指闭合并且提示框尚未显示，则显示提示框
      if (handClosedDetected && !handClosed.value) {
        handClosed.value = true
      }
    }

    canvasCtx.restore()
  })
}

onMounted(() => {
  hands = new Hands({
    locateFile: (file) => {
      return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
    }
  })

  hands.setOptions({
    maxNumHands: 2,  // 支持最多两只手
    modelComplexity: 0,  // 使用低复杂度模型（速度较快）
    minDetectionConfidence: 0.5,  // 最低检测置信度
    minTrackingConfidence: 0.5  // 最低跟踪置信度
  })

  hands.onResults(onResults)

  camera = new Camera(videoElement.value, {
    onFrame: async () => {
      await hands.send({ image: videoElement.value })
    },
    width: 320,
    height: 240,
    frameRate: 30
  })

  camera.start()
})

onUnmounted(() => {
  if (camera) {
    camera.stop()
  }
  if (hands) {
    hands.close()
  }
})
</script>

<style scoped>
.hand-detection {
  position: relative;
  width: 320px;
  height: 240px;
  margin: 0 auto;
}

.input-video {
  position: absolute;
  visibility: hidden;
}

.output-canvas {
  position: absolute;
  transform: scaleX(-1);
}

.alert {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(255, 0, 0, 0.6);
  color: white;
  padding: 10px;
  font-size: 16px;
  border-radius: 5px;
}
</style>
